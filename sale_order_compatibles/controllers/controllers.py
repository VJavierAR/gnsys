# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging, ast
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
_logger = logging.getLogger(__name__)

class SaleOrderCompatibles(http.Controller):
    @http.route('/sale_order_compatibles/sale_order_compatibles/<int:sale_id>', auth='public')
    def index(self, sale_id,**kw):
        p=request.env['sale.order'].search([['id','=',sale_id]])
        uido=request.env.context.get('uid')
        _logger.info(str(uido))
        u=request.env['res.groups'].search([['name','=','ventas autorizacion']]).users.filtered(lambda x:x.id==uido)
        _logger.info(str(u.id))
        if(p.x_studio_tipo_de_solicitud in ["Venta","Venta directa","Arrendamiento","Backup","Demostracion"] and u.id!=False):
            p.action_confirm()
        if(p.x_studio_tipo_de_solicitud == "Cambio" and u.id!=False):
            p.cambio()
        if(p.x_studio_tipo_de_solicitud == "Retiro" and u.id!=False):
            p.retiro()
        if(u.id==False):
            return "No tiene permisos para realizar esta acción"
        name = 'Sale'
        res_model = 'sale.order' 
        view_name = 'studio_customization.sale_order_form_8690a815-6188-42ab-9845-1c18a02ee045'
        view = request.env.ref(view_name)
        return {
            'name': _('Sale'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'view_id': view.id,
            'target': 'current',
            'res_id': sale_id,
            'nodestroy': True
        }    


class SaleOrderCompatiblesCancel(http.Controller):
    @http.route('/sale_order_compatibles/cancel/<int:sale_id>', auth='public')
    def index(self, sale_id,**kw):
        p=request.env['sale.order'].search([['id','=',sale_id]])
        p.action_cancel()
        name = 'Sale'
        res_model = 'sale.order' 
        view_name = 'studio_customization.sale_order_form_8690a815-6188-42ab-9845-1c18a02ee045'
        view = self.env.ref(view_name)
        return {
            'name': _('Sale'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'view_id': view.id,
            'target': 'current',
            'res_id': sale_id,
            'nodestroy': True
        }   
        #return "Orden  "+str(p.name)+" Cancelada"
        #return "HOLA"
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