from odoo import fields, models, api

import datetime
import logging
import calendar

_logger = logging.getLogger(__name__)


class Licencias(models.Model):
    # _name = 'hr.presencialidad'
    _inherit = 'hr.leave'
    _description = 'Description'

    @api.model_create_multi
    def create(self, vals_list):
        v = 0
        h = 9
