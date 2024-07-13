from odoo import models, fields, api
from datetime import timedelta, datetime, date  # Se agrega 'date' aquí
from odoo.exceptions import ValidationError, UserError  # Importaciones combinadas
import logging

_logger = logging.getLogger(__name__)


class CositasDulcesTask(models.Model):
    _inherit = 'project.task'
    employee_id = fields.Many2one('hr.employee', string='Empleado')

    @staticmethod
    def _get_next_friday(start_date, weeks=0):
        _logger.info(f"Iniciando el método _get_next_friday con start_date: {start_date} y weeks: {weeks}")
        try:
            next_friday = start_date + datetime.timedelta((4 - start_date.weekday()) % 7)
            next_friday += datetime.timedelta(weeks=weeks)
            _logger.info(f"El próximo viernes calculado es: {next_friday}")
            return next_friday
        except Exception as e:
            _logger.error(f"Error al calcular el próximo viernes: {e}", exc_info=True)
            raise

    @api.model
    def send_deadline_reminders_prueba(self):
        _logger.info("Iniciando el proceso de envío de correos a empleados con tareas pendientes para hoy.")
        # Obtener la fecha actual
        today = fields.Date.context_today(self)
        project_cositas_dulces = self.env['project.project'].search([('name', '=', 'Cositas Dulces')], limit=1)

        # Buscar tareas cuya fecha de vencimiento sea hoy
        tasks_due_today = self.env['project.task'].search([
            ('date_deadline', '=', today),
            ('project_id', '=', project_cositas_dulces.id)

        ])

        if not tasks_due_today:
            # Si no hay tareas pendientes para hoy, registra un mensaje
            _logger.info("No hay tareas con fecha límite para hoy.")
            return

        # Referencia al template de correo
        template = self.env.ref('cositas_dulces.email_template_employee_reminder')

        # Buscar la última date_deadline asignada en todas las tareas
        last_task_with_deadline = self.env['project.task'].search([('date_deadline', '!=', False)],
                                                                  order='date_deadline desc', limit=1)

        if last_task_with_deadline:
            last_deadline = last_task_with_deadline.date_deadline
            new_deadline = last_deadline + datetime.timedelta(days=7)
        else:
            # Si no hay tareas con fecha límite, establecer la nueva fecha límite a 7 días a partir de hoy
            new_deadline = today + datetime.timedelta(days=7)

        # Recorrer cada tarea pendiente para hoy
        for task in tasks_due_today:
            employee = task.employee_id
            if employee.work_email:
                _logger.info(
                    f"Preparando para enviar correo a {employee.name} ({employee.work_email}) para la tarea {task.name}")
                try:
                    # Enviar el correo
                    template.send_mail(task.id, force_send=True)
                    _logger.info(f"Correo enviado correctamente a {employee.name} para la tarea {task.name}")

                    # Actualizar la date_deadline de la tarea actual con la nueva fecha límite calculada
                    task.date_deadline = new_deadline
                    _logger.info(f"Fecha límite de la tarea {task.name} actualizada a {new_deadline}")

                except Exception as e:
                    _logger.error(f"Error al enviar correo al empleado {employee.name} para la tarea {task.name}: {e}",
                                  exc_info=True)

    @staticmethod
    def get_all_employees(env):
        try:
            _logger.info("Obteniendo todos los empleados")
            employees = env['hr.employee'].search([])
            _logger.info(f"Total de empleados encontrados: {len(employees)}")
            return employees
        except Exception as e:
            _logger.error(f"Error al obtener los empleados: {e}", exc_info=True)
            return []

    @classmethod
    def _create_tasks_for_employees(cls, env):
        try:
            _logger.info("Iniciando la creación de tareas para los empleados")

            employees = cls.get_all_employees(env)
            if not employees:
                _logger.warning("No se encontraron empleados para asignar tareas")
                return

            project = env.ref('cositas_dulces.project_cositas_dulces')
            stage = env.ref('cositas_dulces.project_task_stage_cositas_dulces')

            start_date = date.today()

            for index, employee in enumerate(employees):
                next_friday = cls._get_next_friday(start_date, weeks=index)
                task = env['project.task'].create({
                    'name': employee.name,
                    'project_id': project.id,
                    'stage_id': stage.id,
                    'employee_id': employee.id,
                    'date_deadline': next_friday,
                    'sequence': index
                })
                # Creación de registro en hr.calendario_unificado
                env['hr.calendario_unificado'].create({
                    'id_father': task.id,
                    'name': 'CMT:' + employee.name,
                    'date_from': next_friday,
                    'date_to': next_friday,
                    'descripcion': f"Tarea para {employee.name}",
                    'tipo_evento': 'Cositas Dulces'
                })


                _logger.info(f"Tarea {task} creada para {employee.name} con fecha límite {next_friday}")

        except Exception as e:
            _logger.error(f"Error en _create_tasks_for_employees: {e}", exc_info=True)
            raise

    @staticmethod
    def _get_next_friday(start_date, weeks=0):
        try:
            # Si el día de la semana es mayor que 4 (viernes), sumar una semana adicional para asegurar que el próximo viernes sea realmente el siguiente y no el actual
            if start_date.weekday() >= 4:  # 0 es lunes, 4 es viernes
                weeks += 1
            next_friday = start_date + timedelta((4 - start_date.weekday()) % 7)
            next_friday += timedelta(weeks=weeks)
            return next_friday
        except Exception as e:
            _logger.error(f"Error en _get_next_friday con start_date: {start_date} y weeks: {weeks}: {e}")
            raise  # Propagar la excepción para manejo adicional si es necesario

    def write(self, values):
        # Verificar si 'sequence' está presente en los valores y si es diferente al actual
        sequence_changed = 'sequence' in values and any(record.sequence != values['sequence'] for record in self)
        result = super(CositasDulcesTask, self).write(values)  # Aplicar cambios primero

        if sequence_changed:
            try:
                # Obtener todos los project_ids únicos de las tareas afectadas
                project_ids = set(self.mapped('project_id').ids)
                for project_id in project_ids:
                    _logger.info(f"Comenzando a recalcular fechas para el proyecto {project_id}")
                    # Para cada proyecto, obtener todas sus tareas ordenadas por secuencia
                    tasks = self.env['project.task'].search([('project_id', '=', project_id)], order='sequence asc')
                    start_date = fields.Date.context_today(self)  # O cualquier otra lógica de fecha de inicio
                    for index, task in enumerate(tasks):
                        try:
                            # Asignar nuevas fechas usando _get_next_friday y la secuencia
                            next_friday = self._get_next_friday(start_date, weeks=index)
                            task.date_deadline = next_friday
                            _logger.info(f"Nueva fecha de vencimiento asignada a la tarea {task.name}: {next_friday}")
                        except Exception as e:
                            _logger.error(f"Error al asignar nueva fecha a la tarea {task.name}: {e}")
                for record in self:
                    calendario_unificado_records = self.env['hr.calendario_unificado'].search(
                        [('id_father', '=', record.id)])
                    for calendario_record in calendario_unificado_records:
                        calendario_vals = {}
                        if 'name' in values:
                            # Asumiendo que quieres anteponer 'CMT:' al nombre de la tarea en el calendario unificado
                            calendario_vals['name'] = 'CMT:' + record.name
                        if 'date_deadline' in values:
                            # Usar la fecha de vencimiento de la tarea como 'date_from' y 'date_to' en el calendario unificado
                            calendario_vals['date_from'] = record.date_deadline
                            calendario_vals['date_to'] = record.date_deadline

                        if calendario_vals:
                            # Actualizar el registro en hr.calendario_unificado si hay valores para cambiar
                            calendario_record.write(calendario_vals)
                            _logger.info(f"Actualizado registro en hr.calendario_unificado para la tarea {record.name}")

            except Exception as e:
                _logger.error(f"Error general al recalcular fechas basado en la secuencia: {e}")

        return result  # Devolver el resultado del super().write(values)


def post_init_hook(env):
    _logger.info("Ejecutando el método post-instalación para crear tareas para los empleados")
    env['project.task']._create_tasks_for_employees(env)
