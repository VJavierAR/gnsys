# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import exceptions, _
import logging, ast
import sys
import datetime
import pytz
"""
from odoo import http
from odoo.addons.web.controllers.main import ReportController  # Import the class
"""




class factura(models.Model):
      _inherit = 'account.invoice'
      date_invoice = fields.Date(string='Fecha factura', default=datetime.datetime.now(pytz.utc).strftime('%Y-%m-%d'))
      
      def report_download(self):
        res = super(ReportController, self).report_download()       
        raise exceptions.ValidationError( "no se puede dividir más solo tiene un servicio")    
         #return res

      @api.model
      def create(self,vals):
          fact = super(factura, self).create(vals)
          if fact.x_studio_field_EFIxP:
              if fact.x_studio_field_EFIxP.x_studio_metodo_de_pago=="PPD Pago en parcialidades o diferido" and int(fact.x_studio_field_EFIxP.x_studio_dias_de_credito)<30:
                 raise exceptions.ValidationError("faltan método de pago incorrecto o días de crédico incorrecto")

              if fact.x_studio_field_EFIxP.x_studio_metodo_de_pago=='[None]':
                 raise exceptions.ValidationError("faltan método de pago.")


              if not fact.x_studio_field_EFIxP.partner_id.vat or not len(str(fact.x_studio_field_EFIxP.partner_id.vat))>11:
                 raise exceptions.ValidationError("falta rfc para crear factura valor :"+str(fact.x_studio_field_EFIxP.partner_id.vat))

              if not fact.x_studio_field_EFIxP.x_studio_usocfdi:
                 raise exceptions.ValidationError("faltan usocfdi para crear factura "+str(fact.x_studio_field_EFIxP.x_studio_usocfdi))

              if not fact.x_studio_field_EFIxP.x_studio_forma_de_pago :
                 raise exceptions.ValidationError("faltan forma de pago para crear factura ."+str(fact.x_studio_field_EFIxP.x_studio_forma_de_pago))


              #raise exceptions.ValidationError("faltan forma de pago para crear factura"+str(fact.x_studio_field_EFIxP.partner_id.vat))

          return fact          
     
      @api.multi
      def write(self, vals):
          res = super(factura, self).write(vals)
            #update your custom model's field when the Invoice state is paid
          state = vals.get("state")
          if state == 'cancel':
             mail_template = self.env['mail.template'].search([('id', '=', 61)])
             if mail_template:
                mail_template.write({
                    'email_to': self.x_studio_destinatarios,
                    })
                mail_template.attachment_ids = [(4, 388981)]
                self.env['mail.template'].browse(mail_template.id).send_mail(self.id,force_send=True)    
          res          
         
      @api.multi
      def enviar_factura_timbrada(self, vals):                                        
          mail_template = self.env['mail.template'].search([('id', '=', 61)])
          if mail_template:
             mail_template.write({
                    'email_to': self.x_studio_destinatarios,
                    })
             mail_template.attachment_ids = [(4,  126616)]
             self.env['mail.template'].browse(mail_template.id).send_mail(self.id,force_send=True)              
            
"""         
class CustomController(ReportController):  # Inherit in your custom class

    @http.route('/report/download', auth='user', type='http')
    def report_download(self):
        res = super(CustomController, self).report_download()
        raise exceptions.ValidationError( "no se puede dividir más solo tiene un servicio")    
        # Your code goes here
        return res            
"""
