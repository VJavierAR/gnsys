# -*- coding: utf-8 -*-
from datetime import date
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression

class Compras(http.Controller):
    @http.route('/compras/compras/<int:order_id>', type='http', auth="public", website=True)
    def fun(self,order_id, report_type=None, access_token=None, message=False, download=False, **kw):
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