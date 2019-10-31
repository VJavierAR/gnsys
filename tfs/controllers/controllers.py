# -*- coding: utf-8 -*-
from odoo import http

# class Tfs(http.Controller):
#     @http.route('/tfs/tfs/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tfs/tfs/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tfs.listing', {
#             'root': '/tfs/tfs',
#             'objects': http.request.env['tfs.tfs'].search([]),
#         })

#     @http.route('/tfs/tfs/objects/<model("tfs.tfs"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tfs.object', {
#             'object': obj
#         })