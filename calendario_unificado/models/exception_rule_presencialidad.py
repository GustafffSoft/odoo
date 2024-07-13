from odoo import fields, models, api
from odoo.exceptions import ValidationError
from copy import copy

import datetime
import logging

_logger = logging.getLogger(__name__)


class ExceptoionRulePresencialidad(models.Model):
    _name = 'hr.exception.rule.presencialidad'

    employee_id = fields.Many2one(comodel_name='hr.employee', string='Nombre del empleado', required=True, )
    presencialidad = fields.Selection(string='Presencialidad', help='Seleccion el modo de trabajo',
                                      selection=[('presencial', 'Presencial'), ('remoto', 'Remoto')],
                                      required=False, default='presencial')
    fecha = fields.Date(string="Fecha de cambio", help='Fecha en la que se hara efectivo el cambio de regle')

    @api.constrains('fecha', 'employee_id')
    def _check_unique_fecha(self):
        for record in self:
            if record.fecha:
                duplicate_records = self.env['hr.exception.rule.presencialidad'].search([
                    ('fecha', '=', record.fecha),
                    ('employee_id', '=', record.employee_id.id)
                ])
                if len(duplicate_records) > 1:
                    raise ValidationError("Ya usted registro un cambio de regla para la fecha:" + str(record.fecha))

    @api.model_create_multi
    def create(self, vals_list):
        values = []
        if self.convertir_to_fecha(vals_list[0]['fecha']).date() < self.obtener_fecha_lunes().date():
            raise ValidationError("La fecha: " + vals_list[0][
                'fecha'] + " ya no puede ser programada corresponde a una semana ya trabajada.")

        if self.es_semana_laboral(vals_list[0]['fecha']):
            # employee_id = super().create(vals_list)
            print("Debug: Value of 'self' in create method:", self)

            fecha_con_hora = self.agergar_tiempo_fecha(vals_list[0]['fecha'])

            project = self.env['project.project'].search([('name', '=', 'Presencialidad')], limit=1)

            task_list = self.env['project.task'].search([
                ('project_id', '=', project.id),
                ('date_deadline', '=', fecha_con_hora)
            ])
            task_cambio_regla = self.env['project.task'].search([
                ('project_id', '=', project.id),
                ('date_deadline', '=', fecha_con_hora),
                ('task_type', '=', 'cambio_regla')
            ])

            if len(task_list) == 0:
                # creo la regla
                return super().create(vals_list)
                # raise ValidationError(
                #     "No se han generado los grupos de presencialidad. Contacte con el administrador")

            task_list_ordenada = sorted(task_list, key=lambda x: x.id)

            task_presencial = task_list_ordenada[0]
            task_remoto = task_list_ordenada[1]

            employee_id = self.env['hr.employee'].browse(vals_list[0].get('employee_id'))

            tareas_usuario = self.env['project.task.stage.personal'].search([
                ('user_id', '=', employee_id.user_id.id)
            ])

            flag_presencial = task_presencial.id in tareas_usuario.task_id.ids
            flag_remoto = task_remoto.id in tareas_usuario.task_id.ids
            if vals_list[0]['presencialidad'] == 'presencial' and flag_presencial:
                self.throw_ecception(vals_list, employee_id)
            elif vals_list[0]['presencialidad'] == 'remoto' and flag_remoto:
                self.throw_ecception(vals_list, employee_id)

            if task_cambio_regla:
                # editoo
                self.editar_tarea(fecha_con_hora, task_cambio_regla, employee_id.user_id)
            else:
                self.crear_tarea(fecha_con_hora, employee_id.user_id)

            flag_employee_presencial = task_presencial.user_ids.filtered(
                lambda task: task.id == employee_id.user_id.id)
            flag_employee_remoto = task_remoto.user_ids.filtered(lambda task: task.id == employee_id.user_id.id)

            if flag_employee_presencial and task_presencial.task_type != vals_list[0]['presencialidad']:
                task_remoto.cantidad_personas_tarea += 1
                task_remoto.name = 'Remoto:' + str(task_remoto.cantidad_personas_tarea)
                task_presencial.cantidad_personas_tarea -= 1
                task_presencial.name = 'Presencial:' + str(task_presencial.cantidad_personas_tarea)

                array_auxiliar = copy(task_presencial.user_ids.ids)
                array_auxiliar.remove(flag_employee_presencial.id)
                array_auxiliar2 = copy(task_remoto.user_ids.ids)
                array_auxiliar2.append(flag_employee_presencial.id)

                task_remoto.user_ids = array_auxiliar2
                task_presencial.user_ids = array_auxiliar

                task_remoto.write({
                    'cantidad_personas_tarea': task_remoto.cantidad_personas_tarea,
                    'name': task_remoto.name,
                    'user_ids': [(6, 0, array_auxiliar2)],
                })
                self.editar_evento_calendario(task_remoto)
                task_presencial.write({
                    'cantidad_personas_tarea': task_presencial.cantidad_personas_tarea,
                    'name': task_presencial.name,
                    'user_ids': [(6, 0, array_auxiliar)],
                })
                self.editar_evento_calendario(task_presencial)

            elif flag_employee_remoto and task_remoto.task_type != vals_list[0]['presencialidad']:
                task_presencial.cantidad_personas_tarea += 1
                # values['cantidad_personas_tarea'] = task_presencial.cantidad_personas_tarea
                task_presencial.name = 'Presencial:' + str(task_presencial.cantidad_personas_tarea)
                task_remoto.cantidad_personas_tarea -= 1
                task_remoto.name = 'Remoto:' + str(task_remoto.cantidad_personas_tarea)

                array_auxiliar = copy(task_remoto.user_ids.ids)
                array_auxiliar.remove(flag_employee_remoto.id)
                array_auxiliar2 = copy(task_presencial.user_ids.ids)
                array_auxiliar2.append(flag_employee_remoto.id)

                task_remoto.user_ids = array_auxiliar
                task_presencial.user_ids = array_auxiliar2

                task_remoto.write({
                    'cantidad_personas_tarea': task_remoto.cantidad_personas_tarea,
                    'name': task_remoto.name,
                    'user_ids': [(6, 0, array_auxiliar)],
                })
                self.editar_evento_calendario(task_remoto)
                task_presencial.write({
                    'cantidad_personas_tarea': task_presencial.cantidad_personas_tarea,
                    'name': task_presencial.name,
                    'user_ids': [(6, 0, array_auxiliar2)],
                })
                self.editar_evento_calendario(task_presencial)


            else:
                raise ValidationError(
                    "Ya para esta fecha " + str(vals_list[0][
                                                    'fecha']) + " el usuario: " + employee_id.name + " tiene definido que trabajara de forma " +
                    vals_list[0]['presencialidad'] + ".")
        return super().create(vals_list)

    def es_semana_laboral(self, fecha_dada):
        # Obtener el día de la semana para la fecha actual (0: Lunes, 1: Martes, ..., 4: Viernes)
        fecha_actual = fields.Date.context_today(self)
        # fecha_actual = fields.Date.today()
        # fecha_actual = datetime.date.today()

        dia_semana_actual = datetime.datetime.strptime(str(fecha_actual), '%Y-%m-%d').weekday()

        fecha_dada = datetime.datetime.strptime(str(fecha_dada), '%Y-%m-%d').date()
        # Calcular la fecha del lunes de la semana actual
        lunes_semana_actual = (datetime.datetime.strptime(str(fecha_actual), '%Y-%m-%d') - datetime.timedelta(
            days=dia_semana_actual)).date()

        # fields.Date.context_today(self)
        # fields.Datetime.now()

        # Calcular la fecha del viernes de la semana actual
        viernes_semana_actual = lunes_semana_actual + datetime.timedelta(days=4)

        # Verificar si la fecha dada está dentro de la semana laboral (lunes a viernes)
        if lunes_semana_actual <= fecha_dada <= viernes_semana_actual:
            return True
        else:
            return False

    def agergar_tiempo_fecha(self, fecha):
        time_8_am = datetime.time(8, 0, 0)
        fecha = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
        fecha_con_hora = datetime.datetime.combine(fecha, time_8_am)
        return fecha_con_hora

    def crear_tarea(self, fecha_con_hora, user_id):
        try:
            _logger.info("Iniciando el proceso para visualizar presencialidad")

            project_ref = self.env.ref('calendario_unificado.project_presencialidad_hr')
            task_cambio_regla = self.env.ref('calendario_unificado.project_task_stage_cambio_regla')

            task = self.env['project.task'].create({
                'name': 'Cambio de regla:' + str(1),
                'project_id': project_ref.id,
                'stage_id': task_cambio_regla.id,
                'user_ids': [(6, 0, user_id.ids)],
                # Aquí asignas una lista de IDs de usuarios que cambiaron de echa
                'date_deadline': fecha_con_hora,
                'task_type': 'cambio_regla',
                'cantidad_personas_tarea': 1
                # 'date_deadline': self.next_day(first_day, index)
            })
            self.crear_evento_calendario(task, fecha_con_hora, 'cambio_regla',
                                         'Cantidad de colaboradores que cambiaron de regla')
        except Exception as e:
            _logger.error(f"Error en el proceso: {e}", exc_info=True)
            raise

    def crear_evento_calendario(self, task, fecha, tipo_evento, descripcion):
        visualizacion_unificada = self.env['hr.calendario_unificado'].create({
            'id_father': task.id,
            'name': getattr(task, 'name'),
            'date_from': fecha,
            'date_to': fecha,
            'descripcion': descripcion,
            'tipo_evento': tipo_evento
        })
        hi = 5

    def editar_evento_calendario(self, task):
        evento = self.env['hr.calendario_unificado'].search([
                ('id_father', '=', task.id)
            ])
        evento.write({'name': task.name})

    def editar_tarea(self, fecha_con_hora, task_cambio_regla, user_id):
        _logger.info("Iniciando el proceso para visualizar presencialidad")

        task_cambio_regla.cantidad_personas_tarea += 1
        array_auxiliar = copy(task_cambio_regla.user_ids.ids)
        array_auxiliar.append(user_id.id)
        task_cambio_regla.name = 'Cambio de regla:' + str(task_cambio_regla.cantidad_personas_tarea)

        task_cambio_regla.write({
            'cantidad_personas_tarea': task_cambio_regla.cantidad_personas_tarea,
            'user_ids': [(6, 0, array_auxiliar)],
            'name': task_cambio_regla.name,
        })
        self.editar_evento_calendario(task_cambio_regla)

    def obtener_fecha_lunes(self):
        # Obtener la fecha actual
        hoy = fields.Date.context_today(self)
        # Convertir la fecha actual a objeto datetime
        fecha_actual = self.convertir_to_fecha(hoy)

        # Obtener el día de la semana (lunes = 0, martes = 1, ..., domingo = 6)
        dia_semana = fecha_actual.weekday()
        # Calcular la diferencia de días necesaria para llegar al lunes
        diferencia_lunes = datetime.timedelta(days=dia_semana)

        # Calcular la fecha del lunes
        lunes = fecha_actual - diferencia_lunes

        return lunes

    # datetime.datetime.strptime(str(hoy), '%Y-%m-%d')

    def convertir_to_fecha(self, fecha):
        return datetime.datetime.strptime(str(fecha), '%Y-%m-%d')

    def throw_ecception(self, vals_list, employee_id):
        raise ValidationError(
            "Ya para esta fecha " + str(vals_list[0][
                                            'fecha']) + " el usuario: " + "'" + employee_id.name + "'" + " tiene definido que trabajara de forma " +
            vals_list[0]['presencialidad'] + ".")
