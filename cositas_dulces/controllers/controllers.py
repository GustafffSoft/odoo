# -*- coding: utf-8 -*-
# from odoo import http


# class CositasDulcesIi(http.Controller):
#     @http.route('/cositas_dulces_ii/cositas_dulces_ii', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cositas_dulces_ii/cositas_dulces_ii/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cositas_dulces_ii.listing', {
#             'root': '/cositas_dulces_ii/cositas_dulces_ii',
#             'objects': http.request.env['cositas_dulces_ii.cositas_dulces_ii'].search([]),
#         })

#     @http.route('/cositas_dulces_ii/cositas_dulces_ii/objects/<model("cositas_dulces_ii.cositas_dulces_ii"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cositas_dulces_ii.object', {
#             'object': obj
#         })

