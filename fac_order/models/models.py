# -*- coding: utf-8 -*-

#from odoo import models, fields, api
from odoo import _, models, fields, api, tools

class fac_order(models.Model):
      _inherit = 'sale.order'
#     _name = 'fac_order.fac_order'

      nameDos = fields.Char()
      
     @api.multi 
     def llamado(self):
       for r in self:
          r['x_studio_llenado_de_info_xd']="olo"        
          """ 
          f=len(r.x_studio_servicios_contratos)
          ff=r.x_studio_servicios_contratos
          if f>0:
            h=[]
            g=[]
            p=[]
            for m in ff:
              h.append(m.id)
            g=self.env['sale.subscription.line'].search([('analytic_account_id', '=', int(h[0]))])
            p=self.env['stock.production.lot'].search([('x_studio_suscripcion', '=', int(h[0]))])
            sale=self.env['sale.order'].search([('name', '=', self.name)])
            r['x_studio_llenado_de_info_xd']=str(p)+"olo"
            for t in g:
                self.env['sale.order.line'].create({'order_id': sale.id,'product_id':t.product_id.id})
            for h in p:
                self.env['sale.order.line'].create({'order_id': sale.id,'product_id':h.product_id.id})
          """     
