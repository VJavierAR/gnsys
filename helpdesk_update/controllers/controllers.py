# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging, ast
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
_logger = logging.getLogger(__name__)


class Helpdesk_Controller(http.Controller):
    @http.route('/helpdesk_update/validar_solicitud_de_refacciones/<int:ticket_id>', auth='public')
    def validar_solicitud_de_refacciones(self, sale_id,**kw):
    	_logger.info('3312: validar_solicitud_de_refacciones()')
    	ticket_id = request.env['helpdesk.ticket'].search([['id', '=', ticket_id]])
    	uido = request.env.context.get('uid')
    	_logger.info('3312: usuiaro sesion' + str(uido))
    	ticket_id.x_studio_field_nO7Xg.action_confirm()
    	ticket_id.optimiza_lineas()
    	respuesta = """
    				<div class='row'>
    					<div class='col-sm-12'>
    						<p>
    							Hola, esto fue lo que resulto: """ + str(ticket_id.x_studio_field_nO7Xg.name) + """
    						</p>
    					</div>
    				</div>
    				"""
    	return respuesta


# class Requisicion(http.Controller):
# #     @http.route('/requisicion/requisicion/', auth='public')
# #     def index(self, **kw):
# #         return "Hello, world"

#     @http.route('/requisicion/requisicion/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('requisicion.listing', {
#             'root': '/requisicion/requisicion',
#             'objects': http.request.env['requisicion.requisicion'].search([]),
#         })

    # @http.route('/requisicion/requisicion/objects/<model("requisicion.requisicion"):obj>/', auth='public')
    # def object(self, obj, **kw):
    #     return http.request.render('requisicion.object', {
    #         'object': obj
    #     })