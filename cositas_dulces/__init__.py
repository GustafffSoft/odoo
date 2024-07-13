# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID
from . import controllers
from . import models


def post_init_hook(env):
    models.cositas_dulces_task.post_init_hook(env)

