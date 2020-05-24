# -*- coding: utf-8 -*-
from odoo import http

# class SaleOrderCompatibles(http.Controller):
#     @http.route('/sale_order_compatibles/sale_order_compatibles/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_order_compatibles/sale_order_compatibles/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_order_compatibles.listing', {
#             'root': '/sale_order_compatibles/sale_order_compatibles',
#             'objects': http.request.env['sale_order_compatibles.sale_order_compatibles'].search([]),
#         })

#     @http.route('/sale_order_compatibles/sale_order_compatibles/objects/<model("sale_order_compatibles.sale_order_compatibles"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_order_compatibles.object', {
#             'object': obj
#         })