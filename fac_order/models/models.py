# -*- coding: utf-8 -*-

from odoo import _, models, fields, api, tools
from email.utils import formataddr
from odoo.exceptions import UserError
from odoo import exceptions, _
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)

class fac_order(models.Model):
      _inherit = 'sale.order'

      nameDos = fields.Char()
      
      @api.multi 
      def llamado_boton(self):
        for r in self:                    
          f=len(r.x_studio_servicios_contratos)
          ff=r.x_studio_servicios_contratos
          if f>0:
            h=[]
            g=[]
            p=[]
            for m in ff:
              h.append(m.id)
            g=self.env['sale.subscription.line'].search([('analytic_account_id', '=', int(h[0]))])
            for s in g:
              pp=s.product_id.name
              if pp=='Clic excedente monocromático':    
                 eBN=pp
              if pp=='Clic excedente color':    
                 eColor=pp
              if pp=='Clic monocromática':
                 bolsabn=pp  
              if pp=='Clic color':
                 bolsabn=pp               
               #eBN=g.
               #bolsabn=g[0].
               #bolsacolor=g[0].
            p=self.env['stock.production.lot'].search([('x_studio_suscripcion', '=', int(h[0]))])
            sale=self.env['sale.order'].search([('name', '=', self.name)])
            #for t in g:
            #    self.env['sale.order.line'].create({'order_id': sale.id,'product_id':t.product_id.id})
            for h in p:
                if h.x_studio_color_bn=='B/N':  
                   self.env['sale.order.line'].create({'order_id': sale.id,'product_id':h.product_id.id,'x_studio_field_9nQhR':h.id,'product_uom_qty':h.x_studio_pg_proc,'price_unit':eBN})            
                if h.x_studio_color_bn=='Color':  
                   self.env['sale.order.line'].create({'order_id': sale.id,'product_id':h.product_id.id,'x_studio_field_9nQhR':h.id,'product_uom_qty':h.x_studio_pg_proc_color,'price_unit':eColor})
                   self.env['sale.order.line'].create({'order_id': sale.id,'product_id':h.product_id.id,'x_studio_field_9nQhR':h.id,'product_uom_qty':h.x_studio_pg_proc,'price_unit':eBN})                 
