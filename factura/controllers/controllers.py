# -*- coding: utf-8 -*-
from odoo import http

from odoo import exceptions, _
import logging, ast
import sys

from odoo.addons.web.controllers.main import ReportController  # Import the class



class CustomController(ReportController):  # Inherit in your custom class

    @http.route('/report/download', type='http', auth='user')
    def report_download(self,data, token):
        limit = sys.setrecursionlimit(150000) 
        ress = super(CustomController, self).report_download(data, token)
        limit = sys.setrecursionlimit(150000)         
        #raise exceptions.ValidationError( "no se puede dividir más solo tiene un servicio")    
        # Your code goes here
        return ress            


class Factura(http.Controller):
     
    @http.route('/factura/factura/', auth='public')
    def index(self, **kw):
        return "hahahahah recurción xD "

#     @http.route('/factura/factura/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('factura.listing', {
#             'root': '/factura/factura',
#             'objects': http.request.env['factura.factura'].search([]),
#         })

#     @http.route('/factura/factura/objects/<model("factura.factura"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('factura.object', {
#             'object': obj
#         })
