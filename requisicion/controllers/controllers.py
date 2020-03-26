# -*- coding: utf-8 -*-
from odoo import http

# class Requisicion(http.Controller):
#     @http.route('/requisicion/requisicion/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/requisicion/requisicion/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('requisicion.listing', {
#             'root': '/requisicion/requisicion',
#             'objects': http.request.env['requisicion.requisicion'].search([]),
#         })

# #     @http.route('/requisicion/requisicion/objects/<model("requisicion.requisicion"):obj>/', auth='public')
# #     def object(self, obj, **kw):
# #         return http.request.render('requisicion.object', {
# #             'object': obj
# #         })