# -*- coding: utf-8 -*-
from odoo import http

# class Clientes(http.Controller):
#     @http.route('/clientes/clientes', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/clientes/clientes/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('clientes.listing', {
#             'root': '/clientes/clientes',
#             'objects': http.request.env['clientes.clientes'].search([]),
#         })

#     @http.route('/clientes/clientes/objects/<model("clientes.clientes"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('clientes.object', {
#             'object': obj
#         })
