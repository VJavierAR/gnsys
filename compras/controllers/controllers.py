# -*- coding: utf-8 -*-
from odoo import http

class Compras(http.Controller):
    @http.route('/compras/compras/<int:order_id>', auth='public')
    def fun(self,order_id,**kw):
    	p=self.env['purchase.order'].search([['id','=',order_id]])
    	p.button_confirm()
    	return "Solicitud"+str(p.name)+"Autorizada"


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