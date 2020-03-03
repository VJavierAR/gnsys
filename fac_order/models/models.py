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
      month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
                          (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), 
                          (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], 
                          string='Mes')
      #year = fields.Selection(get_years(), string='Año')
            
            
      def get_years():
        year_list = []
        for i in range(2016, 2036):
           year_list.append((i, str(i)))
        return year_list
      
      
      
      @api.multi 
      def llamado_boton(self):
        for r in self:         
          #
          list = ast.literal_eval(r.x_studio_contratosid)  
          ff=self.env['sale.subscription'].search([('x_studio_referencia_contrato.id', 'in',list)])                                            
          f=len(list)
          if f>0:
            h=[]
            g=[]
            p=[]
            #h.append(m.id)
            sale=self.env['sale.order'].search([('name', '=', self.name)])
            sale.write({'x_studio_factura' : 'si'})
            #
            for m in ff:              
                  p=self.env['stock.production.lot'].search([('x_studio_suscripcion', '=', m.id)])                  
                  procesadasColorTotal=0
                  procesadasColorBN=0
                  serUNO=0
                  serDOS=0
                  serTRES=0
                  serTRESp=0
                  eBN=0
                  eColor=0
                  bolsabn=0
                  bolsacolor=0
                  unidadpreciobn=0
                  unidadprecioColor=0
                  proBN=0
                  proColor=0
                  proBNS=0
                  proColorS=0
                  clickColor=0                  
                  for k in p:
                      self.env['sale.order.detalle'].create({'saleOrder': sale.id
                                                              , 'producto': k.product_id.display_name
                                                               , 'serieEquipo': k.name
                                                               ,'locacion':k.x_studio_locacion_recortada
                                                               , 'ultimaLecturaBN': k.x_studio_ultimalecturam
                                                               , 'lecturaAnteriorBN': k.x_studio_lec_ant_bn
                                                               , 'paginasProcesadasBN': k.x_studio_pg_proc

                                                               , 'ultimaLecturaColor': k.x_studio_ultimalecturacolor
                                                               , 'lecturaAnteriorColor': k.x_studio_lec_ant_color
                                                               , 'paginasProcesadasColor': k.x_studio_pg_proc_color
                                                              })                                     
                      if k.x_studio_color_bn=='B/N':
                         procesadasColorBN=k.x_studio_pg_proc+procesadasColorBN                  
                      if k.x_studio_color_bn=='Color':
                        procesadasColorTotal=k.x_studio_pg_proc_color+procesadasColorTotal
                        procesadasColorBN=k.x_studio_pg_proc+procesadasColorBN                                  
                      #g=self.env['sale.subscription.line'].search([('analytic_account_id', '=', m.id)])
                      #raise exceptions.ValidationError( str(g) )                                   
                  #Costo por página procesada BN o color 10742 o 10743             
                  #Renta base con páginas incluidas BN o color + pag. excedentes 10744 o 10745
                  #renta base + costo de página procesada BN o color 10756 o 10757
                  #Renta base + costo de página procesada BN o color  10748 o 10749
                  #Renta base mas costo de pagina procesada BN o color 10754 o 10755
                  #Renta base con páginas incluidas BN + clic de color + excedentes BN 10758 o 10759                        
                  #Renta global + costo de página procesada BN o color 10750 o 10751

                  #Renta global con páginas incluidas BN o color + pag. Excedentes caso 1 ids 10740 o 10741
                  g=self.env['sale.subscription.line'].search([('analytic_account_id', '=', m.id)])
                  v=[]
                  for j in g:
                      v.append(j.product_id.id)

                  vv=set(v)
                  if 10740 in vv:                           
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
                            if s.price_subtotal>3.0:
                               serTRES=s.product_id.id
                               serTRESp=s.price_unit
                               self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serTRES,'product_uom_qty':1.0,'price_unit':serTRESp})                                                    
                        if procesadasColorBN< bolsabn:
                           self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serUNO,'product_uom_qty':0.0,'price_unit':eBN,'x_studio_bolsa':bolsabn})
                        if procesadasColorBN > bolsabn:
                           self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serUNO,'product_uom_qty':abs(bolsabn-procesadasColorBN),'price_unit':eBN,'x_studio_bolsa':bolsabn})
                        if procesadasColorTotal<bolsacolor:            
                           self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serDOS,'product_uom_qty':0.0,'price_unit':eColor,'x_studio_bolsa':bolsacolor})
                        if procesadasColorTotal > bolsacolor:
                           self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serDOS,'product_uom_qty':abs(bolsacolor-procesadasColorTotal),'price_unit':eColor,'x_studio_bolsa':bolsacolor})                  
                  #xds aqui se divide la renta base y los axecentes se crean 2 facturas xD
                  if 10742 in vv:                           
                        for s in g:
                            pp=s.product_id.name
                            if pp=='Clic excedente monocromático':    
                               eBN=s.price_unit
                            if pp=='Clic excedente color':    
                               eColor=s.price_unit
                            if pp=='Clic monocromática':
                               bolsabn=s.quantity
                               serUNO=s.product_id.id
                               unidadpreciobn=s.price_unit                         
                            if pp=='Clic color':
                               bolsacolor=s.quantity
                               serDOS=s.product_id.id
                               unidadprecioColor=s.price_unit  
                            if s.price_subtotal>3.0:
                               serTRES=s.product_id.id
                               serTRESp=s.price_unit
                               self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serTRES,'product_uom_qty':1.0,'price_unit':serTRESp})
                        for j in p:
                              #self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serTRES,'x_studio_field_9nQhR':j.id,'product_uom_qty':1.0,'price_unit':serTRESp})                      
                              if j.x_studio_pg_proc > 0:
                                 self.env['sale.order.line'].create({'order_id': sale.id,'product_id':j.product_id.id,'product_uom_qty':j.x_studio_pg_proc,'price_unit':unidadpreciobn,'x_studio_bolsa':0.0})
                              if j.x_studio_pg_proc_color > 0:
                                 self.env['sale.order.line'].create({'order_id': sale.id,'product_id':j.product_id.id,'product_uom_qty':j.x_studio_pg_proc_color,'price_unit':unidadprecioColor,'x_studio_bolsa':0.0})

                  if 10744 in vv:                           
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
                            if s.price_subtotal>3.0:                         
                               serTRES=s.product_id.id
                               serTRESp=s.price_unit                                              
                        for j in p:
                              self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serTRES,'x_studio_field_9nQhR':j.id,'product_uom_qty':1.0,'price_unit':serTRESp})                      
                              if j.x_studio_pg_proc > bolsabn:
                                 self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serUNO,'product_uom_qty':abs(bolsabn-procesadasColorBN),'price_unit':eBN,'x_studio_bolsa':bolsabn})
                              if j.x_studio_pg_proc_color > bolsacolor:
                                 self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serDOS,'product_uom_qty':abs(bolsacolor-procesadasColorTotal),'price_unit':eColor,'x_studio_bolsa':bolsacolor})
                  if 10749 in vv or 10748 in vv :                           
                        for s in g:
                            pp=s.product_id.name
                            if pp=='Clic excedente monocromático':    
                               eBN=s.price_unit
                            if pp=='Clic excedente color':    
                               eColor=s.price_unit
                            if pp=='Clic monocromática':
                               bolsabn=s.price_unit
                               serUNO=s.product_id.id
                            if pp=='Clic color':
                               bolsacolor=s.price_unit
                               serDOS=s.product_id.id
                            if s.price_subtotal>3.0:                         
                               serTRES=s.product_id.id
                               serTRESp=s.price_unit                                              
                        for j in p:
                              self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serTRES,'x_studio_field_9nQhR':j.id,'product_uom_qty':1.0,'price_unit':serTRESp})                      
                              if j.x_studio_pg_proc > 0:
                                 self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serUNO,'product_uom_qty':j.x_studio_pg_proc,'price_unit':bolsabn,'x_studio_bolsa':0.0})
                              if j.x_studio_pg_proc_color > 0:
                                 self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serDOS,'product_uom_qty':j.x_studio_pg_proc_color,'price_unit':bolsacolor,'x_studio_bolsa':0.0})

                  if 10750 in vv:                           
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
                            if pp=='ProcesadosBN':
                               proBN=s.price_unit
                               proBNS=s.product_id.id
                            if pp=='ProcesadosColor':
                               proColor=s.price_unit
                               proColorS=s.product_id.id                        
                            if s.price_subtotal>3.0:
                               serTRES=s.product_id.id
                               serTRESp=s.price_unit
                               self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serTRES,'product_uom_qty':1.0,'price_unit':serTRESp})
                        if procesadasColorBN>0:
                           self.env['sale.order.line'].create({'order_id': sale.id,'product_id':proBNS,'product_uom_qty':procesadasColorBN,'price_unit':proBN,'x_studio_bolsa':0.0})
                        if procesadasColorTotal>0:            
                           self.env['sale.order.line'].create({'order_id': sale.id,'product_id':proColorS,'product_uom_qty':procesadasColorTotal,'price_unit':proColor,'x_studio_bolsa':0.0})

                  if 10759 in vv:                           
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
                               clickColor=s.price_unit

                            if s.price_subtotal>3.0:
                               serTRES=s.product_id.id
                               serTRESp=s.price_unit
                               self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serTRES,'product_uom_qty':1.0,'price_unit':serTRESp})
                        if bolsabn<procesadasColorBN:
                           self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serUNO,'product_uom_qty':0.0,'price_unit':eBN,'x_studio_bolsa':bolsabn})
                        if procesadasColorBN > bolsabn:
                           self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serUNO,'product_uom_qty':abs(bolsabn-procesadasColorBN),'price_unit':eBN,'x_studio_bolsa':bolsabn})                  
                        if procesadasColorTotal>0:            
                           self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serDOS,'product_uom_qty':procesadasColorTotal,'price_unit':clickColor,'x_studio_bolsa':0.0})
                  if 10458 in vv:                           
                        for s in g:                         
                            if s.price_subtotal>3.0:
                               serTRES=s.product_id.id
                               serTRESp=s.price_unit
                               self.env['sale.order.line'].create({'order_id': sale.id,'product_id':serTRES,'product_uom_qty':1.0,'price_unit':serTRESp})                                                                          
                                         
            
                  
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
