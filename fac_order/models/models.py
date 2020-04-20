# -*- coding: utf-8 -*-

from odoo import _, models, fields, api, tools
from email.utils import formataddr
from odoo.exceptions import UserError
from odoo import exceptions, _
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)


def get_years():
    year_list = []
    for i in range(2010, 2036):
       year_list.append((i, str(i)))
    return year_list
valores = [('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'), ('04', 'Abril'),
                          ('05', 'Mayo'), ('06', 'Junio'), ('07', 'Julio'), ('08', 'Agosto'),
                          ('09', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')]

class fac_order(models.Model):
      _inherit = 'sale.order'

      nameDos = fields.Char()
      month = fields.Selection(valores,string='Mes')
      year = fields.Selection(get_years(), string='Año')
      excedente=fields.Text(string='Excedentes')
                             
     
     
      @api.multi
      def llamado_boton(self):
        for r in self:        
          #
          list = ast.literal_eval(r.x_studio_contratosid)  
          ff=self.env['servicios'].search([('contrato.id', 'in',list)])                                            
          f=len(list)
          if f>0:
            h=[]
            g=[]
            p=[]
            #h.append(m.id)
            sale=self.env['sale.order'].search([('name', '=', self.name)])
            sale.write({'x_studio_factura' : 'si'})
            perido=r.x_studio_peridotmp
            periodoAnterior=''
            mesA=''
            anioA=''
            i=0
            for f in valores:                
                if f[0]==str(self.month):
                 #raise exceptions.ValidationError( str(self.month) + ' ante '+ str(f[0]) +' fg ' +str(valores[i-1][0]))    
                 mesaA=str(valores[i-1][0])
                i=i+1

            anios=get_years()
            i=0
            if str(self.month)=='01':
                anioA=str(int(self.year)-1)
            else:    
                anioA=str(self.year)
            periodoAnterior= anioA+'-'+mesaA
            
            if self.x_studio_dividir_servicios_1:
               
               serviciosd=self.order_line
               srd=[] 
               for ser in serviciosd:
                   srd.append(ser.x_studio_servicio)
               list_set = set(srd)
               asts=[]
               for sett in list_set:
                   asts.append(sett)  
                
               lenset=len(asts)
               
               servicioshtml='' 
               if lenset==1:
                  raise exceptions.ValidationError( "no se puede dividir más solo tiene un servicio")    
               else:
                  for rs in range(lenset-1):
                      fac = self.env['sale.order'].create({'partner_id' : self.partner_id.id
                                                                 ,'origin' : "dividir por servicios: " + str(self.name)
                                                                 , 'x_studio_tipo_de_solicitud' : 'Arrendamiento'
                                                                 , 'x_studio_requiere_instalacin' : True                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
                                                                 , 'team_id' : 1                                                                  
                                                                })
                      servicioshtml="<a href='https://gnsys-corp.odoo.com/web#id="+str(fac.id)+"&action=1167&model=sale.order&view_type=form&menu_id=406' target='_blank'>"+str(fac.name)+"</a>"+'<br> '+servicioshtml
                      for d in self.order_line:
                          #_logger.info("Informacion entre:"+str(asts[rs])+" "+str(d.x_studio_servicio))
                          if asts[rs]==d.x_studio_servicio:  
                             self.env['sale.order.line'].create({'order_id': fac.id,'x_studio_servicio':d.x_studio_servicio,'x_studio_field_9nQhR':d.x_studio_field_9nQhR.id,'product_id':d.product_id.id,'product_uom_qty':d.product_uom_qty,'price_unit':d.price_unit,'x_studio_bolsa':d.x_studio_bolsa})
                      for det in self.detalle:
                          if asts[rs]==d.servicio:
                             self.env['sale.order.detalle'].create({'saleOrder': fac.id
                                                                       ,'producto': d.producto
                                                                       ,'serieEquipo': d.serieEquipo
                                                                       ,'locacion':d.locacion
                                                                       , 'ultimaLecturaBN': d.ultimaLecturaBN
                                                                       , 'lecturaAnteriorBN': d.lecturaAnteriorBN
                                                                       , 'paginasProcesadasBN': d.paginasProcesadasBN
                                                                       , 'ultimaLecturaColor': d.ultimaLecturaColor
                                                                       , 'lecturaAnteriorColor': d.lecturaAnteriorColor
                                                                       , 'paginasProcesadasColor': d.paginasProcesadasColor
                                                                       , 'servicio':d.servicio
                                                                      })   
                             #self.env['sale.order.detalle'].create({'order_id': fac.id,'x_studio_servicio':d.x_studio_servicio,'x_studio_field_9nQhR':d.x_studio_field_9nQhR.id,'product_id':d.product_id.id,'product_uom_qty':d.product_uom_qty,'price_unit':d.price_unit,'x_studio_bolsa':d.x_studio_bolsa})
                                
                  dejar= asts[lenset-1]                               
                  for quitar in self.order_line:
                      if dejar!=quitar.x_studio_servicio:
                         self.env['sale.order.line'].search([('id', '=', quitar.id)]).unlink()
                  for quitar in self.detalle:
                      if dejar!=quitar.servicio:
                         self.env['sale.order.detalle'].search([('id', '=', quitar.id)]).unlink()
          
                            

                      
                  self.excedente=servicioshtml 
               #self.excedente="<a href='https://gnsys-corp.odoo.com/web#id="+str(fac.id)+"&action=1167&model=sale.order&view_type=form&menu_id=406' target='_blank'>"+str(fac.name)+"</a>"
               
            if self.x_studio_dividir_servicios:
               fac = self.env['sale.order'].create({'partner_id' : self.partner_id.id
                                                                 ,'origin' : "dividir por excedentes: " + str(self.name)
                                                                 , 'x_studio_tipo_de_solicitud' : 'Arrendamiento'
                                                                 , 'x_studio_requiere_instalacin' : True                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
                                                                 , 'team_id' : 1                                                                  
                                                                })
                      
               self.excedente="<a href='https://gnsys-corp.odoo.com/web#id="+str(fac.id)+"&action=1167&model=sale.order&view_type=form&menu_id=406' target='_blank'>"+str(fac.name)+"</a>"
               for d in self.order_line:
                   if d.x_studio_bolsa and d.x_studio_excedente == 'si':  
                      self.env['sale.order.line'].create({'order_id': fac.id,'product_id':11340,'product_uom_qty':d.product_uom_qty,'price_unit':d.price_unit,'x_studio_bolsa':d.x_studio_bolsa})
                      self.env['sale.order.line'].search([('id', '=', d.id)]).unlink()                             
            if self.x_studio_dividir_servicios==False and self.x_studio_dividir_servicios_1==False and len(self.order_line)<1:
               _logger.info("Informacion entre: ") 
               for m in ff:              
                          p=self.env['stock.production.lot'].search([('servicio', '=', m.id)])                  
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
                          bnp=0
                          colorp=0                                
                          for k in p:
                              currentP=self.env['dcas.dcas'].search([('serie','=',k.id),('x_studio_field_no6Rb', '=', perido)],order='x_studio_fecha desc',limit=1)
                              currentPA=self.env['dcas.dcas'].search([('serie','=',k.id),('x_studio_field_no6Rb', '=', periodoAnterior)],order='x_studio_fecha desc',limit=1)
                              cng=int(currentP.contadorMono)
                              cngc=int(currentP.contadorColor)

                              if cng==0:
                                 bnp=0
                              else:
                                 bnp=abs(int(currentPA.contadorMono)-int(currentP.contadorMono))
                              if cng==0:
                                 colorp=0
                              else:
                                 colorp=abs(int(currentPA.contadorColor)-int(currentP.contadorColor))                        



                              self.env['sale.order.detalle'].create({'saleOrder': sale.id
                                                                       ,'producto': k.product_id.display_name
                                                                       ,'serieEquipo': k.name
                                                                       ,'locacion':k.x_studio_locacion_recortada
                                                                       , 'ultimaLecturaBN': currentP.contadorMono
                                                                       , 'lecturaAnteriorBN': currentPA.contadorMono
                                                                       , 'paginasProcesadasBN': bnp
                                                                       , 'ultimaLecturaColor': currentP.contadorColor
                                                                       , 'lecturaAnteriorColor': currentPA.contadorColor
                                                                       , 'paginasProcesadasColor': colorp
                                                                       , 'servicio':m.id
                                                                      })
                              if m.nombreAnte=='Costo por página procesada BN o color':
                                 if k.x_studio_color_bn=='B/N':
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':11396,'product_uom_qty':bnp,'price_unit':m.clickExcedenteBN})                                                    
                                 if k.x_studio_color_bn=='Color':
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':11397,'product_uom_qty':colorp,'price_unit':m.clickExcedenteColor})                                                    
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':11396,'product_uom_qty':bnp,'price_unit':m.clickExcedenteBN})                                                    
                              if m.nombreAnte=='Renta global + costo de página procesada BN o color':
                                 if k.x_studio_color_bn=='B/N':
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':11396,'product_uom_qty':bnp,'price_unit':m.clickExcedenteBN})                                                    
                                 if k.x_studio_color_bn=='Color':
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':11397,'product_uom_qty':colorp,'price_unit':m.clickExcedenteColor})                                                    
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':11396,'product_uom_qty':bnp,'price_unit':m.clickExcedenteBN})                                                                                  
                              if m.nombreAnte=='Renta base + costo de página procesada BN o color':
                                 if k.x_studio_color_bn=='B/N':
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':11396,'product_uom_qty':bnp,'price_unit':m.clickExcedenteBN})                                                    
                                 if k.x_studio_color_bn=='Color':
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':11397,'product_uom_qty':colorp,'price_unit':m.clickExcedenteColor})
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':11396,'product_uom_qty':bnp,'price_unit':m.clickExcedenteBN})                                                    
                                 self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':11398,'product_uom_qty':1,'price_unit':m.rentaMensual})                                                    
                              if m.nombreAnte=='Renta base con páginas incluidas BN o color + pag. excedentes':
                                 if k.x_studio_color_bn=='B/N':
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':11396,'product_uom_qty':bnp,'price_unit':m.clickExcedenteBN,'x_studio_bolsa':m.bolsaBN})                                                    
                                 if k.x_studio_color_bn=='Color':
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':11397,'product_uom_qty':colorp,'price_unit':m.clickExcedenteColor,'x_studio_bolsa':m.bolsaColor})
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':11396,'product_uom_qty':bnp,'price_unit':m.clickExcedenteBN,'x_studio_bolsa':m.bolsaBN})                                                    
                                 self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':11398,'product_uom_qty':1,'price_unit':m.rentaMensual})                                                                            
                             
                              if m.nombreAnte=='Renta base con ML incluidas BN o color + ML. excedentes':
                                 if k.x_studio_color_bn=='B/N':
                                    if m.bolsaBN<bnp:
                                       bnp=bnp-m.bolsaBN
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':11340,'product_uom_qty':bnp,'price_unit':m.clickExcedenteBN,'x_studio_bolsa':m.bolsaBN,'x_studio_excedente':'si'})                                                    
                                 if k.x_studio_color_bn=='Color':
                                    if m.bolsaBN<bnp:
                                       bnp=bnp-m.bolsaBN
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':11340,'product_uom_qty':bnp,'price_unit':m.clickExcedenteBN,'x_studio_bolsa':m.bolsaBN,'x_studio_excedente':'si'})                                                    
                                    if m.bolsaColor<colorp:
                                       colorp=colorp-m.bolsaColor                                    
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':11340,'product_uom_qty':colorp,'price_unit':m.clickExcedenteColor,'x_studio_bolsa':m.bolsaColor,'x_studio_excedente':'si'})
                                 self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':11398,'product_uom_qty':1,'price_unit':m.rentaMensual})                                                                            
                              
                            
                              if k.x_studio_color_bn=='B/N':
                                 procesadasColorBN=bnp+procesadasColorBN                  
                              if k.x_studio_color_bn=='Color':
                                procesadasColorTotal=colorp+procesadasColorTotal
                                procesadasColorBN=bnp+procesadasColorBN                                  
               for j in ff:                      
                     if j.nombreAnte=='Renta global con páginas incluidas BN o color + pag. Excedentes':                        
                        self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'product_id':11395,'product_uom_qty':1.0,'price_unit':j.rentaMensual})                                                    
                        if procesadasColorBN< j.bolsaBN:
                           self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'product_id':11396,'product_uom_qty':0.0,'price_unit':j.clickExcedenteBN,'x_studio_bolsa':j.bolsaBN})
                        if procesadasColorBN > j.bolsaBN:
                           self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'product_id':11396,'product_uom_qty':abs(bolsabn-procesadasColorBN),'price_unit':j.clickExcedenteBN,'x_studio_bolsa':j.bolsaBN,'x_studio_excedente':'si'})
                        if procesadasColorTotal<j.bolsaColor:            
                           self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'product_id':11397,'product_uom_qty':0.0,'price_unit':j.clickExcedenteColor,'x_studio_bolsa':j.bolsaColor})
                        if procesadasColorTotal > j.bolsaColor:
                           self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'product_id':11397,'product_uom_qty':abs(bolsacolor-procesadasColorTotal),'price_unit':j.clickExcedenteColor,'x_studio_bolsa':j.bolsaColor,'x_studio_excedente':'si'})                   
                     if j.nombreAnte=='Renta global + costo de página procesada BN o color':                        
                        self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'product_id':11395,'product_uom_qty':1.0,'price_unit':j.rentaMensual})                                                                                                    
                     if j.tipo=='1':                        
                        self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'product_id':11325,'product_uom_qty':1.0,'price_unit':j.rentaMensual})                                                                                                    
                 
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
      servicio=fields.Integer(string='Servicio')
    
     
     
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
