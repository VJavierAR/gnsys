# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
class Compras(http.Controller):
    @http.route('/compras/compras/<int:purchase_id>', auth='public')
    def index(self,purchase_id ,**kw):
    	p=request.env['purchase.order'].search([['id','=',purchase_id]])
    	p.button_approve()
    	return "Orden de compra "+str(p.name)+" Autorizada"

class Ordenes(http.Controller):
    @http.route('/sale/order/<int:sale_id>', auth='public')
    def index(self,sale_id ,**kw):
    	p=request.env['sale.order'].search([['id','=',sale_id]])
    	if(p.x_studio_tipo_de_solicitud in ["Venta","Venta directa","Arrendamiento"]):
    		p.action_confirm()
    	if(p.x_studio_tipo_de_solicitud =="Cambio"):
    		p.cambio()
    	if(p.x_studio_tipo_solicitud =="Retiro"):
    		p.retiro()
    	return "Orden  "+str(p.name)+" Autorizada"




#     @http.route('/compras/compras/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('compras.listing', {
#             'root': '/compras/compras',
#             'objects': http.request.env['compras.compras'].search([]),
#         })

#     @http.route('/compras/compras/objects/<model("compras.compras"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('compras.object', {
#             'object': obj
#         })