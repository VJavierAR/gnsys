# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import exceptions, _
import logging, ast
import sys
import datetime
import pytz
_logger = logging.getLogger(__name__)
"""
from odoo import http
from odoo.addons.web.controllers.main import ReportController  # Import the class
"""
def get_years():
    year_list = []
    for i in range(2010, 2036):
       year_list.append((i, str(i)))
    return year_list
valores = [('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'), ('04', 'Abril'),
                          ('05', 'Mayo'), ('06', 'Junio'), ('07', 'Julio'), ('08', 'Agosto'),
                          ('09', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')]



class factura(models.Model):
      _inherit = 'account.invoice'
      date_invoice = fields.Date(string='Fecha factura', default=datetime.datetime.now(pytz.utc).strftime('%Y-%m-%d'))
      month = fields.Selection(valores,string='Mes',default='04')
      year = fields.Selection(get_years(), string='Año',default=2020)
      #detalle =  fields.One2many('sale.order.detalle', 'account.Invoice', string='Detalle')
      zeros =  fields.One2many('zeros.lineas', 'accountInv', string='Zeros')
      
      @api.multi
      def llamado_boton_factu(self):
        #raise exceptions.ValidationError( "no se puede dividir más solo tiene un servicio"+self.partner_id.name)    
        for r in self:           
          pbn=0
          pcolor=0
          rentaG=0
          rentaE=0
          spc=0
          tfs=0
          sm=0
          sme=0
          netMa=0
          paginasbn=0
          embeded=0
          cuenta=0
          if str(self.partner_id.razonSocial)=='1':
               pbn=11396
               cuenta=30 
               pcolor=11397
               rentaG=11395
               rentaE=11398
               spc=11325
               tfs=11419
               sm=11420
               sme=12130
               netMa=11421
               paginasbn=11422
               embeded=11423
          if str(self.partner_id.razonSocial)=='2': #Grupo
               pbn=12290
               pcolor=12288
               rentaG=12294
               rentaE=12292
               spc=12296
               tfs=12298
               sm=12300
               sme=12302
               netMa=12304
               paginasbn=12306
               embeded=12308
               impre=12540
               lp=12539 
               cuenta=12216 
          if str(self.partner_id.razonSocial)=='3': #servicios
               pbn=12289
               pcolor=12287
               rentaG=12293
               rentaE=12396
               spc=12295
               tfs=12297
               sm=12299
               sme=12301
               netMa=12303
               paginasbn=12305  
               embeded=12307
               cuenta=12175 
                        
          #list = ast.literal_eval(r.x_studio_contratosid)  
          ff=self.env['servicios'].search([('contrato.id', 'in',self.x_studio_contrato_1.ids)])                                            
          f=len(ff)
          if f>0:
            h=[]
            g=[]
            p=[]
            #h.append(m.id)
            #sale=self.env['sale.order'].search([('name', '=', self.name)])
            #sale.write({'x_studio_factura' : 'si'})
            perido=str(r.year)+"-"+str(r.month)
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
            htmlloca=''                                                                  
            if self.x_studio_contrato_1[0].dividirServicios and len(self.x_studio_detalle)>0 :               
               serviciosd=self.invoice_line_ids
               srd=[] 
               for ser in serviciosd:
                   srd.append(ser.x_studio_id_servicio)
               list_set = set(srd)
               asts=[]
               for sett in list_set:
                   asts.append(sett)  
                
               lenset=len(asts)
               
               servicioshtml='' 
               if lenset==1:
                  raise exceptions.ValidationError( "no se puede dividir más solo tiene un servicio"+str(serviciosd)+"aaaaa")    
               else:
                  for rs in range(lenset-1):                                            
                      a=self.env['account.invoice'].create(
                          
                          {'x_studio_captura':self.x_studio_captura.id,'partner_id':self.partner_id.id,
                           
                           'month':self.month,'year':self.year,'x_studio_periodo_1':self.x_studio_periodo_1
                           
                           ,'company_id':self.company_id.id,'l10n_mx_edi_payment_method_id':self.l10n_mx_edi_payment_method_id.id,'payment_term_id':self.payment_term_id.id,
                           
                           'l10n_mx_edi_usage':self.l10n_mx_edi_usage,'journal_id':self.journal_id.id})                                            
                      self.env.cr.execute("insert into x_account_invoice_contrato_rel (account_invoice_id, contrato_id) values (" +str(a.id) + ", " +  str(self.x_studio_contrato_1[0].id) + ");")                          
                      for d in self.invoice_line_ids:
                          if asts[rs]==d.x_studio_id_servicio:  
                             d.write({'invoice_id': a.id})
                      for z in  self.zeros:
                          if asts[rs]==z.idServicio:
                             z.write({'accountInv':a.id})
                            
                          
                      for det in self.x_studio_detalle:
                          if int(asts[rs])==int(det.servicio):                             
                             det.write({'accountInvoice': a.id                                                                
                                                            })
                      a.compute_taxes()      
               
            
            
            
            if self.x_studio_contrato_1[0].dividirLocalidades and len(self.x_studio_detalle)>0:                
                localidades=self.x_studio_detalle
                loca=[]
                for loc in localidades:
                    loca.append(loc.locacion)
                loca_set=set(loca)
                newso=[]
                for lc in loca_set:
                    newso.append(lc)
                    
                normal=newso.pop(0)    
                camb=normal.replace(' ','',1)
                tamlo=len(newso)
                
                for sale in newso:
                    
                    
                    cambio=sale.replace(' ','',1)
                    
                    
                    part=self.env['res.partner'].search([('parent_id', '=',self.partner_id.id),('name','=',cambio)])
                    
                    local=self.env['account.invoice'].create(
                          
                          {'x_studio_captura':self.x_studio_captura.id,'partner_id':part.id,
                           
                           'month':self.month,'year':self.year,'x_studio_periodo_1':self.x_studio_periodo_1
                           
                           ,'company_id':self.company_id.id,'l10n_mx_edi_payment_method_id':self.l10n_mx_edi_payment_method_id.id,'payment_term_id':self.payment_term_id.id,
                           
                           'l10n_mx_edi_usage':self.l10n_mx_edi_usage,'journal_id':self.journal_id.id})
                    
                    self.env.cr.execute("insert into x_account_invoice_contrato_rel (account_invoice_id, contrato_id) values (" +str(local.id) + ", " +  str(self.x_studio_contrato_1[0].id) + ");")                          
                    for det in localidades:                            
                        if str(sale)==str(det.locacion):
                           det.write({'accountInvoice':local.id}) 
                           #_logger.info('localidades '+str(sale)+str(det.locacion)+str(local.id))
                            
                           for sl in  self.invoice_line_ids :
                               if det.serieEquipo==str(sl.x_studio_serie):                                  
                                  sl.write({'invoice_id':local.id})   
                           for z in self.zeros:
                               if det.serieEquipo==str(z.serie) :                                                                                               
                                  z.write({'invoice_id':local.id})   
                    local.compute_taxes()            
                par=self.env['res.partner'].search([('parent_id', '=',self.partner_id.id),('name','=',camb)])
                self.write({'partner_id':par.id})
                
                
            
            
            if self.x_studio_contrato_1[0].dividirExcedentes and len(self.x_studio_detalle)>0:
               ex=self.env['account.invoice'].create(
                          
                          {'x_studio_captura':self.x_studio_captura.id,'partner_id':self.partner_id.id,
                           
                           'month':self.month,'year':self.year,'x_studio_periodo_1':self.x_studio_periodo_1
                           
                           ,'company_id':self.company_id.id,'l10n_mx_edi_payment_method_id':self.l10n_mx_edi_payment_method_id.id,'payment_term_id':self.payment_term_id.id,
                           
                           'l10n_mx_edi_usage':self.l10n_mx_edi_usage,'journal_id':self.journal_id.id})
               self.env.cr.execute("insert into x_account_invoice_contrato_rel (account_invoice_id, contrato_id) values (" +str(ex.id) + ", " +  str(self.x_studio_contrato_1[0].id) + ");")                          
               #self.excedente="<a href='https://gnsys-corp.odoo.com/web#id="+str(fac.id)+"&action=1167&model=sale.order&view_type=form&menu_id=406' target='_blank'>"+str(fac.name)+"</a>"
               for d in self.invoice_line_ids:
                   if d.product_id.name == 'RENTA EQUIPO':                      
                      d.write({'invoice_id':ex.id})                                            
                      
            
            if self.partner_id  and len(self.x_studio_detalle)==0 :
               #raise exceptions.ValidationError( "no se puede dividir más solo tiene un servicioooo")    
            #if self.x_studio_dividir_servicios==False and self.x_studio_dividir_servicios_1==False and len(self.order_line)<1 and self.x_studio_dividir_localidades==False:
               
               for m in ff:              
                          #p=self.env['stock.production.lot'].search([('servicio', '=', m.id)])                  
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
                        
                          old_timee = datetime.datetime.now()
                          contadores=self.x_studio_captura.dca  
                        
                          for k in contadores:
                              #currentP=self.env['dcas.dcas'].search([('serie','=',k.id),('x_studio_field_no6Rb', '=', perido)],order='x_studio_fecha desc',limit=1)
                              #currentPA=self.env['dcas.dcas'].search([('serie','=',k.id),('x_studio_field_no6Rb', '=', periodoAnterior)],order='x_studio_fecha desc',limit=1)
                              if m.id==int(k.x_studio_servicio):  
                                  cng=k.contadorMono
                                  cngc=k.contadorColor

                                  if cng==0:
                                     bnp=0
                                  else:
                                     bnp=abs(int(k.x_studio_lectura_anterior_bn)-int(k.contadorMono))
                                  if cngc==0:
                                     colorp=0
                                  else:
                                     colorp=abs(int(k.x_studio_lectura_anterior_color)-int(k.contadorColor))                        



                                  detalleC = self.env['sale.order.detalle'].create({'accountInvoice': self.id
                                                                           ,'producto': k.serie.product_id.name
                                                                           ,'serieEquipo': k.serie.name
                                                                           ,'locacion':k.serie.x_studio_locacion_recortada
                                                                           , 'ultimaLecturaBN': k.contadorMono
                                                                           , 'lecturaAnteriorBN': k.x_studio_lectura_anterior_bn
                                                                           , 'paginasProcesadasBN': bnp
                                                                           , 'ultimaLecturaColor': k.contadorColor
                                                                           , 'lecturaAnteriorColor': k.x_studio_lectura_anterior_color
                                                                           , 'paginasProcesadasColor': colorp
                                                                           , 'servicio':m.id
                                                                           , 'ubicacion':k.serie.x_studio_centro_de_costos
                                                                           , 'estado':k.serie.x_studio_estado
                                                                           , 'color':k.serie.x_studio_color_bn        
                                                                          })                          
                                  #raise exceptions.ValidationError( "no se puede dividir más solo tiene un servicio"+ str(m.id)+' '+ str(k.x_studio_servicio) + str(m.id==k.x_studio_servicio) )   
                                  if m.nombreAnte=='Costo por página procesada BN o color' and m.id==int(k.x_studio_servicio):
                                     p=''
                                     if m.contrato.cliente.id==1108:#operadora de hospitales exception
                                        p=' Periodo ' + str(dict(self._fields['month'].selection).get(self.month)) +' de ' + str(self.year)  

                                     if k.x_studio_color_o_bn=='B/N':
                                         if bnp>0: 
                                            inv = self.env['account.invoice.line'].create({'x_studio_id_servicio':m.id,'invoice_id': self.id,'x_studio_id_servicio':m.id,'account_id':cuenta,'name':'(82121500) PAGINAS IMPRESAS NEGRO','x_studio_serie':k.serie.name,'product_id':pbn,'quantity':bnp,'price_unit':m.clickExcedenteBN})                                         
                                            inv.write({ 'invoice_line_tax_ids' : [ (6, 0 , [2] ) ] })                                         
                                         else:
                                            self.env['zeros.lineas'].create({'accountInv': self.id,'idServicio':m.id,'unidad':'ZP','cantidad':0.0,'precioUnitario':m.clickExcedenteBN,'serie':k.serie.name,'descripcion':'(82121500) PAGINAS IMPRESAS NEGRO'})

                                     if k.x_studio_color_o_bn=='Color':
                                         if colorp>0: 
                                            inv=self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'account_id':cuenta,'name':'(82121500) PAGINAS IMPRESAS COLOR','x_studio_serie':k.serie.name,'product_id':pcolor,'quantity':colorp,'price_unit':m.clickExcedenteColor})                                               
                                            inv.write( { 'invoice_line_tax_ids' : [ (6, 0 , [2] ) ] })    
                                         else:
                                            self.env['zeros.lineas'].create({'accountInv': self.id,'idServicio':m.id,'unidad':'ZP','cantidad':0.0,'precioUnitario':m.clickExcedenteColor,'serie':k.serie.name,'descripcion':'(82121500) PAGINAS IMPRESAS COLOR'})   

                                         if bnp>0:
                                            invc=self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'account_id':cuenta,'name':'(82121500) PAGINAS IMPRESAS NEGRO','x_studio_serie':k.serie.name,'product_id':pbn,'quantity':bnp,'price_unit':m.clickExcedenteBN})                                                      
                                            invc.write( { 'invoice_line_tax_ids' : [ (6, 0 , [2] ) ] }) 
                                         else:
                                            self.env['zeros.lineas'].create({'accountInv': self.id,'idServicio':m.id,'unidad':'ZP','cantidad':0.0,'precioUnitario':m.clickExcedenteBN,'serie':k.serie.name,'descripcion':'(82121500) PAGINAS IMPRESAS NEGRO'})   
                #factura = self.id          
                #self.compute_taxes()                                                                                                                                              

                                  if m.nombreAnte=='Renta base + costo de página procesada BN o color' and m.id==int(k.x_studio_servicio):
                                     p=''
                                     if m.contrato.cliente.id==1108:
                                        p=' MODELO '+str(k.serie.product_id.name)+' Período ' + str(dict(self._fields['month'].selection).get(self.month)) +' de ' + str(self.year)
                                     if k.x_studio_color_o_bn=='B/N':
                                        if bnp>0:
                                           self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'x_studio_serie':k.serie.name,'account_id':cuenta,'product_id':pbn,'quantity':bnp,'price_unit':m.clickExcedenteBN,'name':'(82121500) PAGINAS IMPRESAS NEGRO :'+str(bnp)+' NEGRO INCLUYE ('+str(m.bolsaBN)+')  : SERIE:'+k.serie.name+p,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ] })                                                    
                                        else:
                                            self.env['zeros.lineas'].create({'accountInv': self.id,'idServicio':m.id,'unidad':'ZP','cantidad':0.0,'precioUnitario':m.clickExcedenteBN,'serie':k.serie.name,'descripcion':'(82121500) PAGINAS IMPRESAS NEGRO'})

                                     if k.x_studio_color_o_bn=='Color':
                                        if colorp>0:
                                           self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'x_studio_serie':k.serie.name,'account_id':cuenta,'product_id':pcolor,'quantity':colorp,'price_unit':m.clickExcedenteColor,'name':'(82121500) PAGINAS IMPRESAS COLOR: '+str(colorp)+'  INCLUYE ('+str(m.bolsaColor)+') SERIE : '+k.serie.name+p ,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})
                                        else:
                                            self.env['zeros.lineas'].create({'accountInv': self.id,'idServicio':m.id,'unidad':'ZP','cantidad':0.0,'precioUnitario':m.clickExcedenteColor,'serie':k.serie.name,'descripcion':'(82121500) PAGINAS IMPRESAS COLOR'})   

                                        if bnp>0:
                                           self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'x_studio_serie':k.serie.name,'account_id':cuenta,'product_id':pbn,'quantity':bnp,'price_unit':m.clickExcedenteBN,'name':'(82121500) PAGINAS IMPRESAS: '+str(bnp)+' NEGRO INCLUYE ('+str(m.bolsaBN)+')  SERIE:'+k.serie.name +p,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})                                               
                                        else:
                                            self.env['zeros.lineas'].create({'accountInv': self.id,'idServicio':m.id,'unidad':'ZP','cantidad':0.0,'precioUnitario':m.clickExcedenteBN,'serie':k.serie.name,'descripcion':'(82121500) PAGINAS IMPRESAS NEGRO'})
                                     if str(k.serie.x_studio_estado)!='Back-up':   
                                        self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'x_studio_serie':k.serie.name,'account_id':cuenta,'product_id':rentaE,'quantity':1,'price_unit':m.rentaMensual,'name':'(80161801)  RENTA EQUIPO ' +k.serie.x_studio_locacion_recortada+' SERIE: '+k.serie.name +p,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})                                                    
                                        #self.env['account.invoice.line'].create({'invoice_id': sale.id,'x_studio_serie':k.name,'product_id':rentaE,'product_uom_qty':1,'x_studio_cantidad':'1','price_unit':m.rentaMensual,'name':'(80161801)  RENTA EQUIPO ' +k.x_studio_locacion_recortada+' SERIE: '+k.name +p,'discount':int(self.x_studio_descuento)})                                                    
                #self.compute_taxes()                          

                                  if m.id==int(k.x_studio_servicio) and (m.nombreAnte=='Renta base con ML incluidas BN o color + ML. excedentes' or m.nombreAnte=='Renta base con páginas incluidas BN o color + pag. excedentes' ):
                                    if str(k.serie.x_studio_estado)!='Back-up':
                                         p=''
                                         if m.contrato.cliente.id==1108:
                                            p=' MODELO '+str(k.serie.product_id.name)+' Período ' + str(dict(self._fields['month'].selection).get(self.month)) +' de ' +str(self.year)
                                         if k.x_studio_color_o_bn=='B/N':
                                            if m.bolsaBN<bnp:
                                               bnp=bnp-m.bolsaBN
                                               self.env['account.invoice.line'].create({'invoice_id':self.id,'x_studio_serie':k.serie.name,'product_id':pbn,'account_id':cuenta,'quantity':bnp,'price_unit':m.clickExcedenteBN,'x_studio_bolsa':m.bolsaBN,'name':'(82121500) PAGINAS IMPRESAS NEGRO: '+str(bnp)+' INCLUYE ('+str(m.bolsaBN)+') SERIE: '+k.serie.name +p,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})
                                            #aqui tenemos que ver que onda con currente pa and currentp    
                                            else:
                                               self.env['zeros.lineas'].create({'accountInv': self.id,'idServicio':m.id,'unidad':'ZP','cantidad':0.0,'precioUnitario':m.clickExcedenteBN,'serie':k.serie.name,'bolsa':m.bolsaBN,'descripcion':'(82121500) PAGINAS IMPRESAS NEGRO: '+str(abs(int(k.x_studio_lectura_anterior_bn)-int(k.contadorMono)))+' INCLUYE ('+str(m.bolsaBN)+') :'+p})
                                            #else:    
                                            #   self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'x_studio_serie':k.name,'product_id':pbn,'quantity':0,'x_studio_cantidad':'0','price_unit':m.clickExcedenteBN,'x_studio_bolsa':m.bolsaBN,'name':'(82121500) PAGINAS IMPRESAS NEGRO: '+str(abs(int(currentPA.contadorMono)-int(currentP.contadorMono)))+' INCLUYE ('+str(m.bolsaBN)+') SERIE:'+k.name +p})                                                     
                                         if k.x_studio_color_o_bn=='Color':
                                            if m.bolsaBN<bnp:
                                               bnpt=bnp 
                                               bnp=bnp-m.bolsaBN
                                               self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'x_studio_serie':k.serie.name,'product_id':pbn,'account_id':cuenta,'quantity':bnp,'price_unit':m.clickExcedenteBN,'x_studio_bolsa':m.bolsaBN,'x_studio_excedente':'si','name':'(82121500) PAGINAS IMPRESAS NEGRO: '+str(bnpt)+' INCLUYE ('+str(m.bolsaBN)+') SERIE:'+k.serie.name +p,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})                                  
                                            else:
                                               self.env['zeros.lineas'].create({'accountInv': self.id,'idServicio':m.id,'unidad':'ZP','cantidad':0.0,'precioUnitario':m.clickExcedenteBN,'serie':k.serie.name,'bolsa':m.bolsaBN,'descripcion':'(82121500) PAGINAS IMPRESAS NEGRO: '+str(abs(int(k.x_studio_lectura_anterior_bn)-int(k.contadorMono)))+' INCLUYE ('+str(m.bolsaBN)+') :'+p})
                                            #else:
                                            #   self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'x_studio_serie':k.name,'product_id':pbn,'quantity':0,'x_studio_cantidad':'0','price_unit':m.clickExcedenteBN,'x_studio_bolsa':m.bolsaBN,'name':'(82121500) PAGINAS IMPRESAS NEGRO: '+str(abs(int(currentPA.contadorMono)-int(currentP.contadorMono)))+' INCLUYE ('+str(m.bolsaBN)+') SERIE:'+k.name+p })                                                     
                                            if m.bolsaColor<colorp:
                                               clor=colorp 
                                               colorp=colorp-m.bolsaColor                                    
                                               self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'x_studio_serie':k.serie.name,'product_id':pcolor,'account_id':cuenta,'quantity':colorp,'price_unit':m.clickExcedenteColor,'x_studio_bolsa':m.bolsaColor,'name':'(82121500) PAGINAS IMPRESAS COLOR: '+str(clor)+' INCLUYE ('+str(m.bolsaColor)+') SERIE:'+str(k.serie.name) +p,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})    
                                            else:
                                               self.env['zeros.lineas'].create({'accountInv': self.id,'idServicio':m.id,'unidad':'ZP','cantidad':0.0,'precioUnitario':m.clickExcedenteColor,'serie':k.serie.name,'bolsa':m.bolsaColor,'descripcion':'(82121500) PAGINAS IMPRESAS COLOR: '+str(abs(int(k.x_studio_lectura_anterior_color)-int(k.contadorColor)))+' INCLUYE ('+str(m.bolsaColor)+') :'+p})
                                            #else:
                                            #   self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'x_studio_serie':k.name,'product_id':pcolor,'quantity':0,'price_unit':m.clickExcedenteColor,'x_studio_bolsa':m.bolsaColor,'name':'(82121500)  PAGINAS IMPRESAS COLOR: '+str(abs(int(currentPA.contadorColor)-int(currentP.contadorColor)))+' INCLUYE ('+str(m.bolsaColor)+') SERIE:'+k.name+p })                                      
                                         #self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'x_studio_serie':k.name,'product_id':rentaE,'quantity':1,'price_unit':m.rentaMensual,'name':'(80161801)  RENTA EQUIPO ' +k.x_studio_locacion_recortada+' SERIE: '+k.name +p,'discount':int(self.x_studio_descuento)})                                                                                                                                      
                                         self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'x_studio_serie':k.serie.name,'product_id':rentaE,'account_id':cuenta,'quantity':1,'price_unit':m.rentaMensual,'name':'(80161801)  RENTA EQUIPO ' +k.serie.x_studio_locacion_recortada+' SERIE: '+k.serie.name +p,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})             
               new_timee = (old_timee - datetime.datetime.now()).total_seconds()        
                            
               _logger.info('tiempo 11 : ' + str(new_timee)+'   '+str(len(detalleC)))
               for j in ff:                      
                     paso=0
                     if j.nombreAnte=='Renta global con páginas incluidas BN o color + pag. Excedentes': 
                        #raise exceptions.ValidationError( "entre")   
                            
                        p=self.env['stock.production.lot'].search([('servicio', '=', j.id),'|',('x_studio_estado','!=','Back-up'),('x_studio_estado','=',False)])
                        if len(self.x_studio_detalle)>0:
                            
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
                            old_time = datetime.datetime.now()
                            
                            #currentP=self.env['dcas.dcas'].search([('contador_id','=',k.id),('x_studio_field_no6Rb', '=', perido)],order='x_studio_fecha desc',limit=1)
                            #currentPA=self.env['dcas.dcas'].search([('serie','=',k.id),('x_studio_field_no6Rb', '=', periodoAnterior)],order='x_studio_fecha desc',limit=1)
                            for k in self.x_studio_detalle:
                                
                                #currentP=self.env['dcas.dcas'].search([('serie','=',k.id),('x_studio_field_no6Rb', '=', perido)],order='x_studio_fecha desc',limit=1)
                                #currentPA=self.env['dcas.dcas'].search([('serie','=',k.id),('x_studio_field_no6Rb', '=', periodoAnterior)],order='x_studio_fecha desc',limit=1)
                                
                                #cng=int(k.ultimaLecturaBN)
                                
                                #cngc=int(k.contadorColor)                                 
                                
                                #if cng==0:
                                #   bnp=0
                                #else:
                                #   bnp=abs(int(currentPA.contadorMono)-int(currentP.contadorMono))
                                #if cngc==0:
                                #   colorp=0
                                #else:
                                #   colorp=abs(int(currentPA.contadorColor)-int(currentP.contadorColor))
                                
                                if k.color=='B/N':
                                   #raise exceptions.ValidationError( "no se puede dividir más solo tiene un servicio"+str(k.color)) 
                                   procesadasColorBN=k.paginasProcesadasBN+procesadasColorBN
                                if k.color=='Color':
                                   procesadasColorTotal=k.paginasProcesadasColor+procesadasColorTotal
                                   procesadasColorBN=k.paginasProcesadasBN+procesadasColorBN
                            new_time = (old_time - datetime.datetime.now()).total_seconds()        
                            
                            _logger.info('tiempo : ' + str(new_time))
                            
                            if procesadasColorBN< j.bolsaBN :
                               self.env['zeros.lineas'].create({'accountInv': self.id,'idServicio':m.id,'unidad':'ZP','cantidad':0.0,'precioUnitario':j.clickExcedenteBN,'bolsa':j.bolsaBN,'descripcion':'(82121500) PAGINAS IMPRESAS NEGRO : '+str(procesadasColorBN)+' INCLUYE:'+str(j.bolsaBN)})                               
                            if procesadasColorBN > j.bolsaBN:
                               self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'product_id':pbn,'quantity':abs(j.bolsaBN-procesadasColorBN),'price_unit':j.clickExcedenteBN,'x_studio_bolsa':j.bolsaBN,'name':'(82121500) PAGINAS IMPRESAS NEGRO: '+str(procesadasColorBN)+' INCLUYE:'+str(j.bolsaBN),'account_id':cuenta,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})
                            if procesadasColorTotal<j.bolsaColor :            
                               self.env['zeros.lineas'].create({'accountInv': self.id,'idServicio':m.id,'cantidad':0.0,'unidad':'ZP','precioUnitario':j.clickExcedenteColor,'bolsa':j.bolsaColor,'descripcion':'(82121500) PAGINAS IMPRESAS COLOR : '+str(procesadasColorTotal)+' INCLUYE: '+str(j.bolsaColor)})
                               #raise exceptions.ValidationError( "no se puede dividir más solo tiene un servicio"+str(j.clickExcedenteColor))
                            if procesadasColorTotal > j.bolsaColor:
                               self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'product_id':pcolor,'quantity':abs(j.bolsaColor-procesadasColorTotal),'price_unit':j.clickExcedenteColor,'x_studio_bolsa':j.bolsaColor,'name':'(82121500) PAGINAS IMPRESAS COLOR : '+str(abs(bolsacolor-procesadasColorTotal))+' INCLUYE: '+str(j.bolsaColor),'account_id':cuenta,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})                   
                            self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'product_id':rentaG,'quantity':1.0,'price_unit':j.rentaMensual,'name':'(80161801)  RENTA '+ str(len(p))+' EQUIPOS EN GENERAL.','account_id':cuenta,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})
                            
                            
                            #raise exceptions.ValidationError( "no se puede dividir más solo tiene un servicio"+str(new_time))
            
            
                     if j.nombreAnte=='Renta global + costo de página procesada BN o color':                                                
                        p=self.env['stock.production.lot'].search([('servicio', '=', j.id),'|',('x_studio_estado','!=','Back-up'),('x_studio_estado','=',False)])
                        if len(self.x_studio_detalle)>0:
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
                            totalesNegro=0
                            totalesColor=0
                            #raise exceptions.ValidationError( "no se puede dividir más solo tiene un servicio"+str(len(detalleC)))
                            for k in self.x_studio_detalle:
                                #currentP=self.env['dcas.dcas'].search([('serie','=',k.id),('x_studio_field_no6Rb', '=', perido)],order='x_studio_fecha desc',limit=1)
                                #currentPA=self.env['dcas.dcas'].search([('serie','=',k.id),('x_studio_field_no6Rb', '=', periodoAnterior)],order='x_studio_fecha desc',limit=1)
                                #cng=int(k.contadorMono)
                                #cngc=int(k.contadorColor)
                                bnp=k.paginasProcesadasBN 
                                colorp=k.paginasProcesadasColor
                                #if cng==0:
                                #   bnp=0
                                #else:
                                #   bnp=abs(int(currentPA.contadorMono)-int(k.contadorMono))
                                #if cngc==0:
                                #   colorp=0
                                #else:
                                #   colorp=abs(int(currentPA.contadorColor)-int(k.contadorColor))
                                _logger.info('totalng : ' + str(bnp))
                                if k.color=='B/N':
                                   totalesNegro=bnp+totalesNegro
                                if k.color=='Color':
                                   totalesColor=colorp+totalesColor
                                   totalesNegro=bnp+totalesNegro
                                
                            if totalesColor>0:   
                              self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'product_id':pcolor,'quantity':totalesColor,'price_unit':j.clickExcedenteColor,'name':'(82121500) PAGINAS IMPRESAS COLOR : '+str(totalesColor)+' INCLUYE: '+str(m.bolsaColor),'account_id':cuenta,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})
                            if totalesNegro>0:
                              self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'product_id':pbn,'quantity':totalesNegro,'price_unit':j.clickExcedenteBN,'name':'(82121500) PAGINAS IMPRESAS NEGRO : '+str(totalesNegro)+' INCLUYE: '+str(m.bolsaBN),'account_id':cuenta,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})                                                                                  
                            self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'product_id':rentaG,'quantity':1.0,'price_unit':j.rentaMensual,'name':'(80161801) RENTA '+ str(len(p))+' EQUIPOS EN GENERAL.','account_id':cuenta,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})   
            #self.compute_taxes()                                                             
                      
            
               for s in self.x_studio_servicios:
                     if s.nombreAnte=='SERVICIO DE PCOUNTER' or s.nombreAnte=='SERVICIO DE PCOUNTER1' or s.nombreAnte=='ADMINISTRACION DE DOCUMENTOS CON PCOUNTER' or s.nombreAnte=='SERVICIO DE MANTENIMIENTO DE PCOUNTER' or s.nombreAnte=='SERVICIO DE MANTENIMIENTO PCOUNTER' or s.nombreAnte=='RENTA DE LICENCIAMIENTO PCOUNTER':                        
                        self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'product_id':spc ,'quantity':1.0,'price_unit':s.rentaMensual,'name':'(82121500) SERVICIO DE PCOUNTER','account_id':cuenta,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})                                                                                                    
                     if s.nombreAnte=='SERVICIO DE TFS' or s.nombreAnte=='OPERADOR TFS' or s.nombreAnte=='TFS' or s.nombreAnte=='SERVICIO DE TFS ' :                                                                                                                                                     
                        self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'product_id':tfs ,'quantity':1.0,'price_unit':s.rentaMensual,'name':'SERVICIO DE TFS','account_id':cuenta,'invoice_line_tax_ids' : [ (6, 0 , [2, 13] ) ]})                                                            
                        #self.env['account_tax_sale_order_line_rel'].create({'sale_order_line_id': acci.id,'account_tax_id':idtax.id})                                                                                    
                        #self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'product_id':11419 ,'quantity':1.0,'price_unit':s.rentaMensual,'discount':int(self.x_studio_descuento)})                                                                                                    
                     if s.nombreAnte=='SERVICIO DE MANTENIMIENTO':                        
                        self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'product_id':sm ,'quantity':1.0,'price_unit':s.rentaMensual,'name':'SERVICIO DE MANTENIMIENTO','account_id':cuenta,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})                                                                                                    
                     if s.nombreAnte=='LECTORES DE PROXIMIDAD':                        
                        self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'product_id':lp ,'quantity':1.0,'price_unit':s.rentaMensual,'name':'LECTORES DE PROXIMIDAD','account_id':cuenta,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})                                                                                                       
                     if s.nombreAnte=='PAPEL 350,000 HOJAS':                        
                        self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'product_id':impre ,'quantity':1.0,'price_unit':s.rentaMensual,'name':'PAPEL 350,000 HOJAS','account_id':cuenta,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})                                                                                                          
                     if s.nombreAnte=='SOPORTE Y MANTENIMIENTO DE EQUIPOS':                        
                        self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'product_id':sme ,'quantity':1.0,'price_unit':s.rentaMensual,'name':'SOPORTE Y MANTENIMIENTO DE EQUIPOS','account_id':cuenta,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})                                                                                                       
                     if s.nombreAnte=='SERVICIO DE ADMINISTRADOR KM NET MANAGER':                        
                        self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'product_id':netMa ,'quantity':1.0,'price_unit':s.rentaMensual,'name':'SERVICIO DE ADMINISTRADOR KM NET MANAGER','account_id':cuenta,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})                                                                                                    
                     if s.nombreAnte=='PAGINAS IMPRESAS EN BN':                        
                        self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'product_id':paginasbn ,'quantity':int(s.cantidad),'price_unit':s.rentaMensual,'name':'PAGINAS IMPRESAS EN BN','account_id':cuenta,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})                                                                                                    
                     if s.nombreAnte=='RENTA MENSUAL DE LICENCIA  7 EMBEDED' or s.nombreAnte=='RENTA MENSUAL DE LICENCIA  14 EMBEDED' or  s.nombreAnte=='RENTA MENSUAL DE LICENCIA  2 EMBEDED':                        
                        self.env['account.invoice.line'].create({'invoice_id': self.id,'x_studio_id_servicio':m.id,'product_id':embeded ,'quantity':1.0,'price_unit':s.rentaMensual,'name':s.nombreAnte,'account_id':cuenta,'invoice_line_tax_ids' : [ (6, 0 , [2] ) ]})  
            self.compute_taxes()    
    
    
      
      
      
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
     
      """
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
      """

      @api.multi
      def enviar_factura_timbrada_cancelada(self, vals):                                        
          mail_template = self.env['mail.template'].search([('id', '=', 82)])
          if mail_template:
             mail_template.write({
                    'email_to': self.x_studio_destinatarios,
                    })
             #mail_template.attachment_ids = [(4,  126616)]
             self.env['mail.template'].browse(mail_template.id).send_mail(self.id,force_send=True)              
            

      @api.multi
      def enviar_factura_timbrada(self, vals):                                        
          mail_template = self.env['mail.template'].search([('id', '=', 61)])
          if mail_template:
             mail_template.write({
                    'email_to': self.x_studio_destinatarios,
                    })
             #mail_template.attachment_ids = [(4,  126616)]
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
class LineasCero(models.Model):
      _name = 'zeros.lineas'
      _description = 'Consumos en Zero'
    
      accountInv = fields.Many2one('account.invoice', string='Factura')
      cantidad=  fields.Integer(string='Cantidad')
      descripcion=  fields.Text(string='Descripción')
      precioUnitario =  fields.Float(string='Precio Unitario')
      importe =  fields.Float(string='Importe')
      bolsa =  fields.Integer(string='Bolsa')  
      serie = fields.Text(string='Serie')
      unidad = fields.Text(string='Unidad')
      idServicio=fields.Integer(string='id Servicio')
