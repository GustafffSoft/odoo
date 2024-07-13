from odoo import fields, models, api


class VisualizacionUnificada(models.Model):
    _name = 'hr.calendario_unificado'
    _description = 'Visualizacion unificada'

    id_father = fields.Integer(string='ID de la accion que creo el evento')
    name = fields.Char(string='Nombre')
    date_from = fields.Date(string='Fecha inicial', required=True)
    date_to = fields.Date(string='fecha final', required=True)
    tipo_evento = fields.Char(string='Tipo de evento')
    descripcion = fields.Char(string='Descripcion')
