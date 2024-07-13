from odoo import fields, models, api


class FechasImportantes(models.Model):
    _name = 'hr.important_date'
    _description = 'Fechas importantes'

    name = fields.Char(string='Sintesis sobre la fecha', required=True)
    date = fields.Date(string='Date', required=True)
    employee_id = fields.Many2one('hr.employee', string='Empleado')

    def action_boton(self):
        action = self.env['ir.actions.actions']._for_xml_id('hr_proyectos_especiales.action_fechas_importantes_sefipe')
        return action

    @api.model
    def create(self, vals):
        employee = self.env['hr.employee'].browse(vals.get('employee_id'))
        record = super().create(vals)
        year = fields.Date.context_today(self).year
        fecha = fields.Date.from_string(vals.get('date')).replace(year=year)
        self.env['hr.calendario_unificado'].create({
            'id_father': record.id,
            'name': 'FHI:' + getattr(employee, 'name'),
            'date_from': fecha,
            'date_to': fecha,
            'descripcion': vals.get('name', ''),
            'tipo_evento': 'fecha_importante'
        })
        return record

    def write(self, values):
        evento = self.env['hr.calendario_unificado'].search([
            ('id_father', '=', self.id)
        ])
        registros_actualizar = {}
        if values.get('employee_id'):
            employee = self.env['hr.employee'].browse(values.get('employee_id'))
            registros_actualizar['name'] = 'FHI:' + employee.name
        if values.get('date'):
            year = fields.Date.context_today(self).year
            fecha = fields.Date.from_string(values.get('date')).replace(year=year)
            registros_actualizar['date_from'] = fecha
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
