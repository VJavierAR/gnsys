# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import exceptions, _
import logging, ast
import sys

"""
from odoo import http
from odoo.addons.web.controllers.main import ReportController  # Import the class
"""




class factura(models.Model):
      _inherit = 'account.invoice'
      date_invoice = fields.Date(string='Fecha factura', default=datetime.today()) 
      
      def report_download(self):
        res = super(ReportController, self).report_download()       
        raise exceptions.ValidationError( "no se puede dividir más solo tiene un servicio")    
         #return res

            
            
"""         
class CustomController(ReportController):  # Inherit in your custom class

    @http.route('/report/download', auth='user', type='http')
    def report_download(self):
        res = super(CustomController, self).report_download()
        raise exceptions.ValidationError( "no se puede dividir más solo tiene un servicio")    
        # Your code goes here
        return res            
"""
