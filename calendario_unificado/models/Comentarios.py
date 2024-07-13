from odoo import fields, models, api


class Comentarios(models.Model):
    _name = 'hr.comentarios_date'
    _description = 'Comentarios del trabajador'

    name = fields.Char(string='Comentario  especial en la fecha', required=True)
    date = fields.Date(string='Date', required=True)
    employee_id = fields.Many2one('hr.employee', string='Empleado')

    def create(self, vals):
        employee = self.env['hr.employee'].browse(vals.get('employee_id'))
        record = super().create(vals)
        self.env['hr.calendario_unificado'].create({
            'id_father': record.id,
            'name': 'CMT:' + getattr(employee, 'name'),
            'date_from': vals.get('date', ''),
            'date_to': vals.get('date', ''),
            'descripcion': vals.get('name', ''),
            'tipo_evento': 'comentarios'
        })
        return record

    def write(self, values):
        evento = self.env['hr.calendario_unificado'].search([
            ('id_father', '=', self.id)
        ])
        registros_actualizar = {}
        if values.get('employee_id'):
            employee = self.env['hr.employee'].browse(values.get('employee_id'))
            registros_actualizar['name'] = 'CMT:' + employee.name
        if values.get('date'):
            registros_actualizar['date_from'] = values.get('date')
        if values.get('name'):
            registros_actualizar['descripcion'] = values.get('name')

        evento.write(registros_actualizar)
        return super().write(values)

    def unlink(self):
        evento = self.env['hr.calendario_unificado'].search([
            ('id_father', '=', self.id)
        ])
        evento.unlink()
        super().unlink()
