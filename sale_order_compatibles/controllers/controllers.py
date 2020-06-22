# -*- coding: utf-8 -*-
from odoo import http

class SaleOrderCompatibles(http.Controller):
    @http.route('/sale_order_compatibles/sale_order_compatibles/<int:sale_id>', auth='public')
    def index(self, **kw):
        p=request.env['sale.order'].search([['id','=',sale_id]])
        if(p.x_studio_tipo_solicitud in ["Venta","Venta directa","Arrendamiento"]):
            p.action_confirm()
        if(p.x_studio_tipo_solicitud == "Cambio"):
            p.cambio()
        if(p.x_studio_tipo_solicitud == "Retiro"):
            p.retiro()
        return "Orden  "+str(p.name)+" Autorizada"
# class SaleOrderCompatibles(http.Controller):
#     @http.route('/sale/order/<int:sale_id>', auth='public')
#     def index(self,sale_id ,**kw):
#         p=request.env['sale.order'].search([['id','=',sale_id]])
#         if(p.x_studio_tipo_solicitud in ["Venta","Venta directa","Arrendamiento"]):
#             p.action_confirm()
#         if(p.x_studio_tipo_solicitud == "Cambio"):
#             p.cambio()
#         if(p.x_studio_tipo_solicitud == "Retiro"):
#             p.retiro()
#         return "Orden  "+str(p.name)+" Autorizada"




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