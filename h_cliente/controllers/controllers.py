# -*- coding: utf-8 -*-
# from odoo import http


# class HCliente(http.Controller):
#     @http.route('/h_cliente/h_cliente/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/h_cliente/h_cliente/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('h_cliente.listing', {
#             'root': '/h_cliente/h_cliente',
#             'objects': http.request.env['h_cliente.h_cliente'].search([]),
#         })

#     @http.route('/h_cliente/h_cliente/objects/<model("h_cliente.h_cliente"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('h_cliente.object', {
#             'object': obj
#         })
