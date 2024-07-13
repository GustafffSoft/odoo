from odoo import fields, models, api

import datetime
import logging
import calendar

_logger = logging.getLogger(__name__)


class Presencialidad(models.Model):
    # _name = 'hr.presencialidad'
    _inherit = 'project.task'
    _description = 'Description'

    task_type = fields.Char(string='Tipo de Tarea')
    cantidad_personas_tarea = fields.Integer(string='Cantidad de Personas en actividad')

    # @api.model
    def _compute_presencial_remoto_count(self):
        presencial_count = {}
        remoto_count = {}
        cambio_regla_count = {}

        lunes_presencial_count = 0
        martes_presencial_count = 0
        miercoles_presencial_count = 0
        jueves_presencial_count = 0
        viernes_presencial_count = 0

        lunes_remoto_count = 0
        martes_remoto_count = 0
        miercoles_remoto_count = 0
        jueves_remoto_count = 0
        viernes_remoto_count = 0

        array_ids_presencial_lunes = []
        array_ids_presencial_martes = []
        array_ids_presencial_miercoles = []
        array_ids_presencial_jeuves = []
        array_ids_presencial_viernes = []

        array_ids_remoto_lunes = []
        array_ids_remoto_martes = []
        array_ids_remoto_miercoles = []
        array_ids_remoto_jueves = []
        array_ids_remoto_viernes = []

        array_ids_cambio_fecha_lunes = []
        array_ids_cambio_fecha_martes = []
        array_ids_cambio_fecha_miercoles = []
        array_ids_cambio_fecha_jueves = []
        array_ids_cambio_fecha_viernes = []

        cambio_regla_lunes_count = 0
        cambio_regla_martes_count = 0
        cambio_regla_miercoles_count = 0
        cambio_regla_jueves_count = 0
        cambio_regla_viernes_count = 0

        # cambio_regla_count = self.get_result_reglas_auxiliar_lista()
        employees = self.env['hr.employee'].search([])

        # compruebo
        for employee in employees:
            employee_excpetion_rules = self.get_list_exception_rule_en_semana_laboral(employee)
            for day in ['lunes', 'martes', 'miercoles', 'jueves', 'viernes']:

                employee_cambio_regla = self.get_cambio_regla_day(employee_excpetion_rules, day)
                presencialidad = getattr(employee, day)

                if day == 'lunes':
                    if employee_cambio_regla:
                        presencialidad = employee_cambio_regla.presencialidad
                        cambio_regla_lunes_count += 1
                        array_ids_cambio_fecha_lunes.append(employee.user_id.id)

                    if presencialidad == 'presencial':
                        lunes_presencial_count += 1
                        array_ids_presencial_lunes.append(employee.user_id.id)
                    else:
                        lunes_remoto_count += 1
                        array_ids_remoto_lunes.append(employee.user_id.id)

                elif day == 'martes':
                    if employee_cambio_regla:
                        presencialidad = employee_cambio_regla.presencialidad
                        cambio_regla_martes_count += 1
                        array_ids_cambio_fecha_martes.append(employee.user_id.id)

                    if presencialidad == 'presencial':
                        martes_presencial_count += 1
                        array_ids_presencial_martes.append(employee.user_id.id)
                    else:
                        martes_remoto_count += 1
                        array_ids_remoto_martes.append(employee.user_id.id)

                elif day == 'miercoles':
                    if employee_cambio_regla:
                        presencialidad = employee_cambio_regla.presencialidad
                        cambio_regla_miercoles_count += 1
                        array_ids_cambio_fecha_miercoles.append(employee.user_id.id)

                    if presencialidad == 'presencial':
                        miercoles_presencial_count += 1
                        array_ids_presencial_miercoles.append(employee.user_id.id)
                    else:
                        miercoles_remoto_count += 1
                        array_ids_remoto_miercoles.append(employee.user_id.id)

                elif day == 'jueves':

                    if employee_cambio_regla:
                        presencialidad = employee_cambio_regla.presencialidad
                        cambio_regla_jueves_count += 1
                        array_ids_cambio_fecha_jueves.append(employee.user_id.id)

                    if presencialidad == 'presencial':
                        jueves_presencial_count += 1
                        array_ids_presencial_jeuves.append(employee.user_id.id)
                    else:
                        jueves_remoto_count += 1
                        array_ids_remoto_jueves.append(employee.user_id.id)

                elif day == 'viernes':

                    if employee_cambio_regla:
                        presencialidad = employee_cambio_regla.presencialidad
                        cambio_regla_viernes_count += 1
                        array_ids_cambio_fecha_viernes.append(employee.user_id.id)

                    if presencialidad == 'presencial':
                        viernes_presencial_count += 1
                        array_ids_presencial_viernes.append(employee.user_id.id)
                    else:
                        viernes_remoto_count += 1
                        array_ids_remoto_viernes.append(employee.user_id.id)

        if cambio_regla_lunes_count > 0:
            cambio_regla_count['lunes'] = {
                'count': cambio_regla_lunes_count,
                'ids': array_ids_cambio_fecha_lunes
            }
        if cambio_regla_martes_count > 0:
            cambio_regla_count['martes'] = {
                'count': cambio_regla_martes_count,
                'ids': array_ids_cambio_fecha_martes
            }
        if cambio_regla_miercoles_count > 0:
            cambio_regla_count['miercoles'] = {
                'count': cambio_regla_miercoles_count,
                'ids': array_ids_cambio_fecha_miercoles
            }
        if cambio_regla_jueves_count > 0:
            cambio_regla_count['jueves'] = {
                'count': cambio_regla_jueves_count,
                'ids': array_ids_cambio_fecha_jueves
            }
        if cambio_regla_viernes_count > 0:
            cambio_regla_count['viernes'] = {
                'count': cambio_regla_viernes_count,
                'ids': array_ids_cambio_fecha_viernes
            }

        presencial_count['lunes'] = {
            'count': lunes_presencial_count,
            'ids': array_ids_presencial_lunes
        }
        presencial_count['martes'] = {
            'count': martes_presencial_count,
            'ids': array_ids_presencial_martes
        }
        presencial_count['miercoles'] = {
            'count': miercoles_presencial_count,
            'ids': array_ids_presencial_miercoles
        }
        presencial_count['jueves'] = {
            'count': jueves_presencial_count,
            'ids': array_ids_presencial_jeuves
        }
        presencial_count['viernes'] = {
            'count': viernes_presencial_count,
            'ids': array_ids_presencial_viernes
        }

        remoto_count['lunes'] = {
            'count': lunes_remoto_count,
            'ids': array_ids_remoto_lunes
        }
        remoto_count['martes'] = {
            'count': martes_remoto_count,
            'ids': array_ids_remoto_martes
        }
        remoto_count['miercoles'] = {
            'count': miercoles_remoto_count,
            'ids': array_ids_remoto_miercoles
        }
        remoto_count['jueves'] = {
            'count': jueves_remoto_count,
            'ids': array_ids_remoto_jueves
        }
        remoto_count['viernes'] = {
            'count': viernes_remoto_count,
            'ids': array_ids_remoto_viernes
        }

        self.crear_tarea(presencial_count, remoto_count, cambio_regla_count)

    def get_list_exception_rule_en_semana_laboral(self, employee):
        fecha_inicial = self.obtener_fecha_para_dia_semana('lunes')
        fecha_final = self.obtener_fecha_para_dia_semana('viernes')

        exception_rules = self.env['hr.exception.rule.presencialidad'].search([
            ('employee_id', '=', employee.id),
        ])
        result = exception_rules.filtered(lambda e: self.es_semana_laboral(e.fecha))
        return result
        # return exception_rules

    def get_cambio_regla_day(self, employee_excpetion_rules, day):
        if employee_excpetion_rules:
            return employee_excpetion_rules.filtered(lambda e: self.get_dia_semana_fecha(e.fecha) == day)

    def if_empleado_has_exception_rule(self, employee):
        return True

    def crear_tarea(self, presencial_count, remoto_count, cambio_regla_count):
        try:
            _logger.info("Iniciando el proceso para visualizar presencialidad")

            project_ref = self.env.ref('calendario_unificado.project_presencialidad_hr')

            task_presencial = self.env.ref('calendario_unificado.project_task_stage_presencial')
            task_remoto = self.env.ref('calendario_unificado.project_task_stage_remoto')
            task_cambio_regla = self.env.ref('calendario_unificado.project_task_stage_cambio_regla')

            # Obtener el número de semanas en el mes actual
            # year = datetime.datetime.now().year
            # month = datetime.datetime.now().month
            # num_weeks = len(calendar.monthcalendar(year, month))
            # first_day = datetime.datetime(year, month, 1).date()

            # var = self.next_day(first_day, index)
            fecha_lunes = self.obtener_fecha_para_dia_semana('lunes')

            index = 0
            # for i in range(0, num_weeks):
            for day, data in presencial_count.items():
                fecha = self.next_day(fecha_lunes, index)
                task = self.env['project.task'].create({
                    'name': 'Presencial:' + str(data['count']),
                    # 'presencialidad': 'presencial',
                    'project_id': project_ref.id,
                    'stage_id': task_presencial.id,
                    'user_ids': [(6, 0, data['ids'])],  # Aquí asignas una lista de IDs de usuarios
                    'date_deadline': self.agregar_tiempo(fecha),
                    'task_type': 'presencial',
                    'cantidad_personas_tarea': str(data['count'])
                    # 'date_deadline': self.next_day(first_day, index)
                })
                self.crear_evento_calendario(task, fecha, tipo_evento='trabajo_presencial',
                                             descripcion='Cantidad de colaboradores trabajando en la oficina')

                index += 1

            index = 0
            # for i in range(0, num_weeks):
            for day, data in remoto_count.items():
                fecha = self.next_day(fecha_lunes, index)
                task = self.env['project.task'].create({
                    'name': 'Remoto:' + str(data['count']),
                    # 'presencialidad': 'remoto',
                    'project_id': project_ref
                    .id,
                    'stage_id': task_remoto.id,
                    'user_ids': [(6, 0, data['ids'])],  # Aquí asignas una lista de IDs de usuarios
                    'date_deadline': self.agregar_tiempo(fecha),
                    'task_type': 'remoto',
                    'cantidad_personas_tarea': str(data['count'])
                    # 'date_deadline': self.next_day(first_day, index)
                })
                self.crear_evento_calendario(task, fecha, tipo_evento='trabajo_remoto',
                                             descripcion='Cantidad de colaboradores trabajando en la casa')
                index += 1

            index = 0
            # if flag_hay_cambio_fecha:
            for day, data in cambio_regla_count.items():
                fecha = self.next_day(fecha_lunes, index)
                task = self.env['project.task'].create({
                    'name': 'Cambio de regla:' + str(data['count']),
                    'project_id': project_ref.id,
                    'stage_id': task_cambio_regla.id,
                    'user_ids': [(6, 0, data['ids'])],
                    # Aquí asignas una lista de IDs de usuarios que cambiaron de echa
                    'date_deadline': self.agregar_tiempo(fecha),
                    'task_type': 'cambio_regla',
                    'cantidad_personas_tarea': str(data['count'])
                    # 'date_deadline': self.next_day(first_day, index)
                })
                self.crear_evento_calendario(task, fecha, tipo_evento='cambio_regla',
                                             descripcion='Cantidad de colaboradores que cambiaron de regla')
                index += 1

        except Exception as e:
            _logger.error(f"Error en el proceso de visualizacion: {e}", exc_info=True)
            raise

    def crear_evento_calendario(self, task, fecha, tipo_evento, descripcion):
        self.env['hr.calendario_unificado'].create({
            'id_father': task.id,
            'name': getattr(task, 'name'),
            'date_from': fecha,
            'date_to': fecha,
            'descripcion': descripcion,
            'tipo_evento': tipo_evento
        })

    def get_dia_semana_fecha(self, fecha):
        # dia_semana_numero = datetime.datetime.strptime(str(fecha), '%Y-%m-%d').weekday()
        dia_semana_numero = fields.Datetime.from_string(fecha).weekday()
        nombres_dias_semana = ["lunes", "martes", "miercoles", "jueves", "viernes", "sábado", "domingo"]
        return nombres_dias_semana[dia_semana_numero]

    def es_semana_laboral(self, fecha_dada):
        # Obtener la fecha actual
        # fecha_actual = fields.Date.today()
        # Obtener el día de la semana para la fecha actual (0: Lunes, 1: Martes, ..., 4: Viernes)
        # fecha_actual = fields.Datetime.now()
        #
        # fecha_dada = datetime.datetime.strptime(str(fecha_dada, '%Y-%m-%d').date()
        # # fecha_actual = fields.Date.context_today(self)
        # dia_semana_actual = datetime.datetime.strptime(str(fecha_actual), '%Y-%m-%d').weekday()
        # # dia_semana_actual = datetime.datetime.strptime(str(fecha_actual), '%Y-%m-%d').weekday()
        #
        # # Calcular la fecha del lunes de la semana actual
        # lunes_semana_actual = (datetime.datetime.strptime(str(fecha_actual), '%Y-%m-%d') - datetime.timedelta(
        #     days=dia_semana_actual)).date()
        #
        # # fields.Date.context_today(self)
        # # fields.Datetime.now()
        #
        # # Calcular la fecha del viernes de la semana actual
        # viernes_semana_actual = lunes_semana_actual + datetime.timedelta(days=4)
        # Obtener la fecha actual
        fecha_actual = fields.Date.context_today(self)

        # Convertir la fecha actual a un objeto datetime
        fecha_actual_datetime = fields.Datetime.from_string(fecha_actual)

        # Obtener el día de la semana para la fecha actual (0: Lunes, 1: Martes, ..., 4: Viernes)
        dia_semana_actual = fecha_actual_datetime.weekday()

        # Calcular la fecha del lunes de la semana actual
        lunes_semana_actual = fecha_actual_datetime - datetime.timedelta(days=dia_semana_actual)

        # Calcular la fecha del viernes de la semana actual
        viernes_semana_actual = lunes_semana_actual + datetime.timedelta(days=4)

        # Verificar si la fecha dada está dentro de la semana laboral (lunes a viernes)
        return lunes_semana_actual <= self.agregar_tiempo(fecha_dada) <= viernes_semana_actual

        # # Verificar si la fecha dada está dentro de la semana laboral (lunes a viernes)
        # if lunes_semana_actual <= fecha_dada <= viernes_semana_actual:
        #     return True
        # else:
        #     return False

    def next_day(self, d, index):
        # time_8_am = datetime.time(8, 0, 0)
        # next_datetime = datetime.datetime.combine(d, time_8_am)
        next_datetime = d + datetime.timedelta(days=index)
        return next_datetime

    def agregar_tiempo(self, date):
        time_8_am = datetime.time(8, 0, 0)
        return datetime.datetime.combine(date, time_8_am)

    def obtener_fecha_para_dia_semana(self, dia_semana):
        # Diccionario para mapear nombres de días de la semana a números
        dias_semana = {
            'lunes': 0,
            'martes': 1,
            'miercoles': 2,
            'jueves': 3,
            'viernes': 4
        }
        # Obtener el número correspondiente al día de la semana especificado

        dia_semana_numero = dias_semana.get(dia_semana.lower())

        if dia_semana_numero is None:
            raise ValueError("El nombre del día de la semana proporcionado no es válido.")

        # Obtener el día de la semana actual como un número (lunes = 0, martes = 1, ..., domingo = 6)
        dia_actual = fields.Datetime.now().weekday()
        # dia_actual = datetime.datetime.now().weekday()

        # Calcular la diferencia de días entre el día actual y el día especificado
        diferencia_dias = dia_semana_numero - dia_actual

        # Obtener la fecha correspondiente al día de la semana especificado
        fecha_correspondiente = fields.Datetime.now() + datetime.timedelta(days=diferencia_dias)
        # fecha_correspondiente = datetime.datetime.now() + datetime.timedelta(days=diferencia_dias)

        return fecha_correspondiente.date()
