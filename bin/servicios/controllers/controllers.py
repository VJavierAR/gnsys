# -*- coding: utf-8 -*-
from odoo import http

# class Servicios(http.Controller):
#     @http.route('/servicios/servicios/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/servicios/servicios/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('servicios.listing', {
#             'root': '/servicios/servicios',
#             'objects': http.request.env['servicios.servicios'].search([]),
#         })

#     @http.route('/servicios/servicios/objects/<model("servicios.servicios"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('servicios.object', {
#             'object': obj
#         })