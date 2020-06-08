# -*- coding: utf-8 -*-
import werkzeug

from odoo import http
from odoo.http import request

from odoo.addons.web.controllers.main import make_conditional, get_last_modified
from odoo.addons.web.controllers.main import manifest_glob, concat_xml
from odoo.addons.web.controllers.main import WebClient

class ComprasAU(http.Controller):
    
    @http.route('/compras/compras/', type='https', auth="none")
    def fun(self, **kw):
        return "Hello, world"

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