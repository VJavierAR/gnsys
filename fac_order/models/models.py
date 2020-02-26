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
            p=self.env['stock.production.lot'].search([('x_studio_suscripcion', '=', int(h[0]))])
            sale=self.env['sale.order'].search([('name', '=', self.name)])
            procesadasColorTotal=0
            procesadasColorBN=0
            for k in p:                  
                if k.x_studio_color_bn=='B/N':
                   procesadasColorTotal=k.x_studio_pg_proc_color+procesadasColorTotal                  
                if k.x_studio_color_bn=='Color':
                  procesadasColorTotal=k.x_studio_pg_proc_color+procesadasColorTotal
                  procesadasColorBN=k.x_studio_pg_proc+procesadasColorBN                                  
                g=self.env['sale.subscription.line'].search([('analytic_account_id', '=', int(h[0]))])
                #raise exceptions.ValidationError( str(g) )                                 
                serUNO=0
                serDOS=0
                eBN=0
                eColor=0
                bolsabn=0
                bolsacolor=0  
                for s in g:
                   pp=s.product_id.name
                   if pp=='Clic excedente monocromático':    
                      eBN=s.price_unit
                   if pp=='Clic excedente color':    
                      eColor=s.price_unit
                   if pp=='Clic monocromática':
                      bolsabn=s.quantity
                      serUNO=s.product_id.id
                   if pp=='Clic color':
                      bolsacolor=s.quantity
                      serDOS=s.product_id.id
                #raise exceptions.ValidationError( str(g)+" "+str(serUNO)+" , "+str(sale.id)+",  "+ str(procesadasColorBN)+",  "+str(eBN))                             
                self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serUNO,'product_uom_qty':procesadasColorBN,'price_unit':eBN})      
                self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serDOS,'product_uom_qty':procesadasColorTotal,'price_unit':eColor})
                #self.env['sale.order.line'].create({'order_id': sale.id,'product_id':h.product_id.id,'x_studio_field_9nQhR':h.id,'product_uom_qty':h.x_studio_pg_proc_color,'price_unit':eColor})

            
            
            
                  
      detalle =  fields.One2many('sale.order.detalle', 'saleOrder', string='Order Lines')
                  
class detalle(models.Model):
      _name = 'sale.order.detalle'
      _description = 'Detalle Orden'
      
      saleOrder = fields.Many2one('sale.order', string='Pedido de venta')
      
      serieEquipo = fields.Text(string="Serie")
      producto = fields.Text(string="Producto")
      locacion = fields.Text(string="Locación")
      
      ultimaLecturaBN = fields.Integer(string='Última lectura monocromatico')
      lecturaAnteriorBN = fields.Integer(string='Lectura anterior monocromatico')
      paginasProcesadasBN = fields.Integer(string='Páginas procesadas monocromatico')
      
      ultimaLecturaColor = fields.Integer(string='última lectura color')
      lecturaAnteriorColor = fields.Integer(string='Lectura anterior color')
      paginasProcesadasColor = fields.Integer(string='Páginas procesadas color')
      
      periodo = fields.Text(string="Periodo")
      
      
      @api.multi 
      def probar(self):
        for r in self:                    
          f=len(r.x_studio_servicios_contratos)
          ff=r.x_studio_servicios_contratos
          if f>0:
            h=[]
            p=[]
            for m in ff:
              h.append(m.id)
            p=self.env['stock.production.lot'].search([('x_studio_suscripcion', '=', int(h[0]))])
            sale=self.env['sale.order'].search([('name', '=', self.name)])
            for h in p:
                  self.env['sale.order.detalle'].create({'saleOrder': sale.id
                                                         , 'producto': h.product_id.display_name
                                                         , 'serieEquipo': h.name
                                                         
                                                         , 'ultimaLecturaBN': h.x_studio_ultimalecturam
                                                         , 'lecturaAnteriorBN': h.x_studio_lec_ant_bn
                                                         , 'paginasProcesadasBN': h.x_studio_pg_proc
                                                         
                                                         , 'ultimaLecturaColor': h.x_studio_ultimalecturacolor
                                                         , 'lecturaAnteriorColor': h.x_studio_lec_ant_color
                                                         , 'paginasProcesadasColor': h.x_studio_pg_proc_color
                                                        })            
