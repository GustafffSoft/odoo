from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import datetime

_logger = logging.getLogger(__name__)


class EmployeeExtension(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def create(self, vals):
        try:
            _logger.info("Creando nuevo empleado")
            new_employee = super(EmployeeExtension, self).create(vals)

            project = self.env['project.project'].search([('name', '=', 'Cositas Dulces')], limit=1)
            if project:
                # Buscar la última fecha de deadline en las tareas del proyecto
                last_task = self.env['project.task'].search([('project_id', '=', project.id)],
                                                            order='date_deadline desc', limit=1)
                last_date = last_task.date_deadline if last_task else fields.Date.today()

                # Calcular el siguiente viernes después de la última fecha
                days_until_friday = (4 - last_date.weekday()) % 7
                next_friday = last_date + datetime.timedelta(days=days_until_friday)
                if days_until_friday == 0:  # Si ya es viernes, mover al próximo viernes
                    next_friday += datetime.timedelta(days=7)
                last_sequence = self.env['project.task'].search([('project_id', '=', project.id)],
                                                                order='sequence desc', limit=1).sequence
                new_sequence = last_sequence + 1 if last_sequence else 1
                # Crear la tarea con la nueva fecha de deadline
                self.env['project.task'].create({
                    'name': 'Cositas Dulces:' + new_employee.name,
                    'project_id': project.id,
                    'employee_id': new_employee.id,
                    'date_deadline': next_friday,
                    'sequence': new_sequence,
                })
                _logger.info(f"Tarea creada para el nuevo empleado con fecha límite {next_friday}")
            else:
                _logger.warning("Proyecto 'Cositas Dulces' no encontrado")

            return new_employee

        except Exception as e:
            _logger.error(f"Error al crear empleado: {e}")
            raise ValidationError("Error al crear empleado: {}".format(e))
