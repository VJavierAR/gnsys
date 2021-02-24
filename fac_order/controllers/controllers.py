# -*- coding: utf-8 -*-
from odoo import http

# class FacOrder(http.Controller):
#     @http.route('/fac_order/fac_order/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fac_order/fac_order/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fac_order.listing', {
#             'root': '/fac_order/fac_order',
#             'objects': http.request.env['fac_order.fac_order'].search([]),
#         })

#     @http.route('/fac_order/fac_order/objects/<model("fac_order.fac_order"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fac_order.object', {
#             'object': obj
#         })