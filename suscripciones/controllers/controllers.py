# -*- coding: utf-8 -*-
from odoo import http

# class Suscripdiones(http.Controller):
#     @http.route('/suscripdiones/suscripdiones/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/suscripdiones/suscripdiones/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('suscripdiones.listing', {
#             'root': '/suscripdiones/suscripdiones',
#             'objects': http.request.env['suscripdiones.suscripdiones'].search([]),
#         })

#     @http.route('/suscripdiones/suscripdiones/objects/<model("suscripdiones.suscripdiones"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('suscripdiones.object', {
#             'object': obj
#         })