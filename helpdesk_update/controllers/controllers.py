# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging, ast
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
_logger = logging.getLogger(__name__)




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