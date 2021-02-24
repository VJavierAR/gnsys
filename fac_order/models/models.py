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
      month = fields.Selection(valores,string='Mes',default='04')
      year = fields.Selection(get_years(), string='Año',default=2020)
      excedente=fields.Text(string='Excedentes')
                             
     
      @api.multi 
      def cambiaPeriodo(self):
        lineas=self.order_line
        nuevomes= str(dict(self._fields['month'].selection).get(self.month))
        for l in lineas:
            s=''
            s=str(l.name)
            if 'Período' in s:
                ar=s.split('Período')
                arr=ar[1].split(' ')
                new=s.replace(arr[1],nuevomes)
                l.write({'name':new})

        
        
      @api.multi
      def llamado_boton(self):
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
          if str(self.partner_id.razonSocial)=='1':
               pbn=11396
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
            htmlloca=''
            if self.x_studio_dividir_localidades:                
                localidades=self.detalle
                loca=[]
                for loc in localidades:
                    loca.append(loc.locacion)
                loca_set=set(loca)
                newso=[]
                for lc in loca_set:
                    newso.append(lc)
                newso.pop(0)    
                tamlo=len(newso)                    
                for sale in newso:
                    local = self.env['sale.order'].create({'partner_id' : self.partner_id.id
                                                                 , 'origin' : "dividir por localidades: " + str(self.name)
                                                                 , 'x_studio_factura':'si'                                                                                                                             
                                                                 ,'month':self.month
                                                                 ,'year':self.year
                                                                })
                    self.env.cr.execute("insert into x_contrato_sale_order_rel (sale_order_id, contrato_id) values (" +str(local.id) + ", " +  str(r.x_studio_contratosid).replace("[","").replace("]","") + ");")                                        
                    htmlloca="<a href='https://gnsys-corp.odoo.com/web#id="+str(local.id)+"&action=1167&model=sale.order&view_type=form&menu_id=406' target='_blank'>"+str(local.name)+"</a>"+'<br> '+htmlloca
                    for det in localidades:                            
                        if str(sale)==str(det.locacion):
                           det.write({'saleOrder':local.id}) 
                           for sl in  self.order_line:
                               if det.serieEquipo==str(sl.x_studio_field_9nQhR.name):                                                             
                                  sl.write({'order_id':local.id})                                                                                                                                                                            
                self.excedente=htmlloca            
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
                                                                 , 'team_id' : 1
                                                                 , 'x_studio_factura':'si'
                                                                 ,'month':self.month
                                                                 ,'year':self.year
                                                                })
                      self.env.cr.execute("insert into x_contrato_sale_order_rel (sale_order_id, contrato_id) values (" +str(fac.id) + ", " +  str(r.x_studio_contratosid).replace("[","").replace("]","") + ");")                                         
                      servicioshtml="<a href='https://gnsys-corp.odoo.com/web#id="+str(fac.id)+"&action=1167&model=sale.order&view_type=form&menu_id=406' target='_blank'>"+str(fac.name)+"</a>"+'<br> '+servicioshtml
                      for d in self.order_line:
                          #_logger.info("Informacion entre:"+str(asts[rs])+" "+str(d.x_studio_servicio))
                          if asts[rs]==d.x_studio_servicio:  
                             self.env['sale.order.line'].create({'order_id': fac.id,'x_studio_servicio':d.x_studio_servicio,'x_studio_field_9nQhR':d.x_studio_field_9nQhR.id,'product_id':d.product_id.id,'x_studio_cantidad':d.product_uom_qty,'product_uom_qty':d.product_uom_qty,'price_unit':d.price_unit,'x_studio_bolsa':d.x_studio_bolsa})
                      for det in self.detalle:
                          #_logger.info("Informacion entre:"+str(asts[rs])+" "+str(det.servicio))
                          if int(asts[rs])==int(det.servicio):
                             
                             self.env['sale.order.detalle'].create({'saleOrder': fac.id
                                                                       ,'producto': det.producto
                                                                       ,'serieEquipo': det.serieEquipo
                                                                       ,'locacion':det.locacion
                                                                       , 'ultimaLecturaBN': det.ultimaLecturaBN
                                                                       , 'lecturaAnteriorBN': det.lecturaAnteriorBN
                                                                       , 'paginasProcesadasBN': det.paginasProcesadasBN
                                                                       , 'ultimaLecturaColor': det.ultimaLecturaColor
                                                                       , 'lecturaAnteriorColor': det.lecturaAnteriorColor
                                                                       , 'paginasProcesadasColor': det.paginasProcesadasColor
                                                                       , 'servicio':det.servicio
                                                                      , 'ubicacion':det.ubicacion
                                                                      })   
                             #self.env['sale.order.detalle'].create({'order_id': fac.id,'x_studio_servicio':d.x_studio_servicio,'x_studio_field_9nQhR':d.x_studio_field_9nQhR.id,'product_id':d.product_id.id,'product_uom_qty':d.product_uom_qty,'price_unit':d.price_unit,'x_studio_bolsa':d.x_studio_bolsa})
                                
                  dejar= asts[lenset-1]
                  qs=[]
                  qd=[]
                  for quitar in self.order_line:
                      if dejar!=quitar.x_studio_servicio:
                         qs.append(quitar.id)   
                  
                  self.env['sale.order.line'].search([('id', 'in', qs)]).unlink()
                  #    return werkzeug.utils.redirect('/signage/admin/menu/%s/edit' % signage.id)
                  for quitard in self.detalle:
                      if int(dejar)!=int(quitard.servicio):                            
                         qd.append(quitard.id)
                  self.env['sale.order.detalle'].search([('id', 'in', qd)]).unlink()
          
                            

                      
                  self.excedente=servicioshtml 
               #self.excedente="<a href='https://gnsys-corp.odoo.com/web#id="+str(fac.id)+"&action=1167&model=sale.order&view_type=form&menu_id=406' target='_blank'>"+str(fac.name)+"</a>"
               
            if self.x_studio_dividir_servicios:
               fac = self.env['sale.order'].create({'partner_id' : self.partner_id.id
                                                                 ,'origin' : "dividir por excedentes: " + str(self.name)
                                                                 , 'x_studio_tipo_de_solicitud' : 'Arrendamiento'
                                                                 , 'x_studio_requiere_instalacin' : True                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
                                                                 , 'team_id' : 1
                                                                 , 'x_studio_factura':'si'
                                                                 ,'month':self.month
                                                                 ,'year':self.year
                                                                })
               self.env.cr.execute("insert into x_contrato_sale_order_rel (sale_order_id, contrato_id) values (" +str(fac.id) + ", " +  str(r.x_studio_contratosid).replace("[","").replace("]","") + ");")       
               self.excedente="<a href='https://gnsys-corp.odoo.com/web#id="+str(fac.id)+"&action=1167&model=sale.order&view_type=form&menu_id=406' target='_blank'>"+str(fac.name)+"</a>"
               for d in self.order_line:
                   if d.x_studio_excedente != 'si':
                      #checar aqui los colores 
                      d.write({'order_id':fac.id})  
                      #self.env['sale.order.line'].create({'order_id': fac.id,'product_id':11396,'product_uom_qty':d.product_uom_qty,'price_unit':d.price_unit,'x_studio_bolsa':d.x_studio_bolsa})
                    
                      #self.env['sale.order.line'].search([('id', '=', d.id)]).unlink()                             
            if self.x_studio_dividir_servicios==False and self.x_studio_dividir_servicios_1==False and len(self.order_line)<1 and self.x_studio_dividir_localidades==False:
               
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
                              if cngc==0:
                                 colorp=0
                              else:
                                 colorp=abs(int(currentPA.contadorColor)-int(currentP.contadorColor))                        



                              self.env['sale.order.detalle'].create({'saleOrder': sale.id
                                                                       ,'producto': k.product_id.name
                                                                       ,'serieEquipo': k.name
                                                                       ,'locacion':k.x_studio_locacion_recortada
                                                                       , 'ultimaLecturaBN': currentP.contadorMono
                                                                       , 'lecturaAnteriorBN': currentPA.contadorMono
                                                                       , 'paginasProcesadasBN': bnp
                                                                       , 'ultimaLecturaColor': currentP.contadorColor
                                                                       , 'lecturaAnteriorColor': currentPA.contadorColor
                                                                       , 'paginasProcesadasColor': colorp
                                                                       , 'servicio':m.id
                                                                       , 'ubicacion':k.x_studio_centro_de_costos
                                                                      })
                              if m.nombreAnte=='Costo por página procesada BN o color':
                                 p=''
                                 if m.contrato.cliente.id==1108:
                                    p=' Periodo ' + str(dict(self._fields['month'].selection).get(self.month)) +' de ' + str(self.year)  
                                 if k.x_studio_color_bn=='B/N':
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_excedente':'si','x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':pbn,'product_uom_qty':bnp,'price_unit':m.clickExcedenteBN,'x_studio_cantidad':str(bnp)})                                                    
                                 if k.x_studio_color_bn=='Color':
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_excedente':'si','x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':pcolor,'product_uom_qty':colorp,'price_unit':m.clickExcedenteColor,'x_studio_cantidad':str(colorp)})                                                    
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_excedente':'si','x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':pbn,'product_uom_qty':bnp,'price_unit':m.clickExcedenteBN,'x_studio_cantidad':str(bnp)})                                                                                  
                                 
                              if m.nombreAnte=='Renta base + costo de página procesada BN o color':
                                 p=''
                                 if m.contrato.cliente.id==1108:
                                    p=' MODELO '+str(k.product_id.name)+' Período ' + str(dict(self._fields['month'].selection).get(self.month)) +' de ' + str(self.year)
                                 if k.x_studio_color_bn=='B/N':
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_excedente':'si','x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':pbn,'product_uom_qty':bnp,'price_unit':m.clickExcedenteBN,'name':'(82121500) PAGINAS IMPRESAS NEGRO :'+str(bnp)+' NEGRO INCLUYE ('+str(m.bolsaBN)+')  : SERIE:'+k.name+p ,'x_studio_cantidad':str(bnp)})                                                    
                                 if k.x_studio_color_bn=='Color':
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_excedente':'si','x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':pcolor,'product_uom_qty':colorp,'price_unit':m.clickExcedenteColor,'name':'(82121500) PAGINAS IMPRESAS COLOR: '+str(colorp)+'  INCLUYE ('+str(m.bolsaColor)+') SERIE : '+k.name+p ,'x_studio_cantidad':str(colorp)})
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_excedente':'si','x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':pbn,'product_uom_qty':bnp,'price_unit':m.clickExcedenteBN,'name':'(82121500) PAGINAS IMPRESAS: '+str(bnp)+' NEGRO INCLUYE ('+str(m.bolsaBN)+')  SERIE:'+k.name +p,'x_studio_cantidad':str(bnp)})                                                     
                                 if str(k.x_studio_estado)!='Back-up':   
                                    self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':rentaE,'product_uom_qty':1,'x_studio_cantidad':'1','price_unit':m.rentaMensual,'name':'(80161801)  RENTA EQUIPO ' +k.x_studio_locacion_recortada+' SERIE: '+k.name +p,'discount':int(self.x_studio_descuento)})                                                    
                              if m.nombreAnte=='Renta base con ML incluidas BN o color + ML. excedentes' or m.nombreAnte=='Renta base con páginas incluidas BN o color + pag. excedentes':
                                if str(k.x_studio_estado)!='Back-up':
                                     p=''
                                     if m.contrato.cliente.id==1108:
                                        p=' MODELO '+str(k.product_id.name)+' Período ' + str(dict(self._fields['month'].selection).get(self.month)) +' de ' +str(self.year)
                                     if k.x_studio_color_bn=='B/N':
                                        if m.bolsaBN<bnp:
                                           bnp=bnp-m.bolsaBN
                                           self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_excedente':'si','x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':pbn,'product_uom_qty':bnp,'x_studio_cantidad':str(bnp),'price_unit':m.clickExcedenteBN,'x_studio_bolsa':m.bolsaBN,'name':'(82121500) PAGINAS IMPRESAS NEGRO: '+str(bnp)+' INCLUYE ('+str(m.bolsaBN)+') SERIE: '+k.name +p})                                                     
                                        else:    
                                           self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_excedente':'si','x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':pbn,'product_uom_qty':0,'x_studio_cantidad':'0','price_unit':m.clickExcedenteBN,'x_studio_bolsa':m.bolsaBN,'name':'(82121500) PAGINAS IMPRESAS NEGRO: '+str(abs(int(currentPA.contadorMono)-int(currentP.contadorMono)))+' INCLUYE ('+str(m.bolsaBN)+') SERIE:'+k.name +p})                                                     
                                     if k.x_studio_color_bn=='Color':
                                        if m.bolsaBN<bnp:
                                           bnpt=bnp 
                                           bnp=bnp-m.bolsaBN
                                           self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':pbn,'product_uom_qty':bnp,'x_studio_cantidad':str(bnp),'price_unit':m.clickExcedenteBN,'x_studio_bolsa':m.bolsaBN,'x_studio_excedente':'si','name':'(82121500) PAGINAS IMPRESAS NEGRO: '+str(bnpt)+' INCLUYE ('+str(m.bolsaBN)+') SERIE:'+k.name +p})                                                    
                                        else:
                                           self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_excedente':'si','x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':pbn,'product_uom_qty':0,'x_studio_cantidad':'0','price_unit':m.clickExcedenteBN,'x_studio_bolsa':m.bolsaBN,'name':'(82121500) PAGINAS IMPRESAS NEGRO: '+str(abs(int(currentPA.contadorMono)-int(currentP.contadorMono)))+' INCLUYE ('+str(m.bolsaBN)+') SERIE:'+k.name+p })                                                     
                                        if m.bolsaColor<colorp:
                                           clor=colorp 
                                           colorp=colorp-m.bolsaColor                                    
                                           self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':pcolor,'product_uom_qty':colorp,'x_studio_cantidad':str(colorp),'price_unit':m.clickExcedenteColor,'x_studio_bolsa':m.bolsaColor,'x_studio_excedente':'si','name':'(82121500) PAGINAS IMPRESAS COLOR: '+str(clor)+' INCLUYE ('+str(m.bolsaColor)+') SERIE:'+k.name +p})
                                        else:
                                           self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_excedente':'si','x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':pcolor,'product_uom_qty':0,'x_studio_cantidad':'0','price_unit':m.clickExcedenteColor,'x_studio_bolsa':m.bolsaColor,'name':'(82121500)  PAGINAS IMPRESAS COLOR: '+str(abs(int(currentPA.contadorColor)-int(currentP.contadorColor)))+' INCLUYE ('+str(m.bolsaColor)+') SERIE:'+k.name+p })                                      
                                     self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':m.id,'x_studio_field_9nQhR':k.id,'product_id':rentaE,'product_uom_qty':1,'x_studio_cantidad':'1','price_unit':m.rentaMensual,'name':'(80161801)  RENTA EQUIPO ' +k.x_studio_locacion_recortada+' SERIE: '+k.name +p,'discount':int(self.x_studio_descuento)})                                                                                                                                      
               for j in ff:                      
                     if j.nombreAnte=='Renta global con páginas incluidas BN o color + pag. Excedentes':                                                                        
                        p=self.env['stock.production.lot'].search([('servicio', '=', j.id),'|',('x_studio_estado','!=','Back-up'),('x_studio_estado','=',False)])
                        if len(p)>0:
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
                                if cngc==0:
                                   colorp=0
                                else:
                                   colorp=abs(int(currentPA.contadorColor)-int(currentP.contadorColor))
                                if k.x_studio_color_bn=='B/N':
                                   procesadasColorBN=bnp+procesadasColorBN                  
                                if k.x_studio_color_bn=='Color':
                                   procesadasColorTotal=colorp+procesadasColorTotal
                                   procesadasColorBN=bnp+procesadasColorBN       
                            if procesadasColorBN< j.bolsaBN :
                               self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':j.id,'product_id':pbn,'product_uom_qty':0.0,'x_studio_cantidad':'0','price_unit':j.clickExcedenteBN,'x_studio_bolsa':j.bolsaBN,'name':'(82121500) PAGINAS IMPRESAS NEGRO : '+str(procesadasColorBN)+' INCLUYE:'+str(j.bolsaBN)})
                            if procesadasColorBN > j.bolsaBN:
                               self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':j.id,'product_id':pbn,'product_uom_qty':abs(j.bolsaBN-procesadasColorBN),'x_studio_cantidad':str(abs(j.bolsaBN-procesadasColorBN)),'price_unit':j.clickExcedenteBN,'x_studio_bolsa':j.bolsaBN,'x_studio_excedente':'si','name':'(82121500) PAGINAS IMPRESAS NEGRO: '+str(procesadasColorBN)+' INCLUYE:'+str(j.bolsaBN)})
                            if procesadasColorTotal<j.bolsaColor :            
                               self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':j.id,'product_id':pcolor,'product_uom_qty':0.0,'x_studio_cantidad':'0','price_unit':j.clickExcedenteColor,'x_studio_bolsa':j.bolsaColor,'name':'(82121500) PAGINAS IMPRESAS COLOR : '+str(procesadasColorTotal)+' INCLUYE: '+str(j.bolsaColor)})
                            if procesadasColorTotal > j.bolsaColor:
                               self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':j.id,'product_id':pcolor,'product_uom_qty':abs(j.bolsaColor-procesadasColorTotal),'x_studio_cantidad':str(abs(j.bolsaColor-procesadasColorTotal)),'price_unit':j.clickExcedenteColor,'x_studio_bolsa':j.bolsaColor,'x_studio_excedente':'si','name':'(82121500) PAGINAS IMPRESAS COLOR : '+str(abs(bolsacolor-procesadasColorTotal))+' INCLUYE: '+str(j.bolsaColor)})                   
                            self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':j.id,'product_id':rentaG,'product_uom_qty':1.0,'x_studio_cantidad':'1','price_unit':j.rentaMensual,'name':'(80161801)  RENTA '+ str(len(p))+' EQUIPOS EN GENERAL.'})
                     if j.nombreAnte=='Renta global + costo de página procesada BN o color':                                                
                        p=self.env['stock.production.lot'].search([('servicio', '=', j.id),'|',('x_studio_estado','!=','Back-up'),('x_studio_estado','=',False)])
                        if len(p)>0:
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
                            
                            for k in p:
                                currentP=self.env['dcas.dcas'].search([('serie','=',k.id),('x_studio_field_no6Rb', '=', perido)],order='x_studio_fecha desc',limit=1)
                                currentPA=self.env['dcas.dcas'].search([('serie','=',k.id),('x_studio_field_no6Rb', '=', periodoAnterior)],order='x_studio_fecha desc',limit=1)
                                cng=int(currentP.contadorMono)
                                cngc=int(currentP.contadorColor)

                                if cng==0:
                                   bnp=0
                                else:
                                   bnp=abs(int(currentPA.contadorMono)-int(currentP.contadorMono))
                                if cngc==0:
                                   colorp=0
                                else:
                                   colorp=abs(int(currentPA.contadorColor)-int(currentP.contadorColor))
                                
                                if k.x_studio_color_bn=='B/N':
                                   totalesNegro=bnp+totalesNegro
                                if k.x_studio_color_bn=='Color':
                                   totalesColor=colorp+totalesColor
                                   totalesNegro=bnp+totalesNegro
                                _logger.info("Informacion entre:"+str(m.clickExcedenteColor))
                            self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':j.id,'x_studio_field_9nQhR':k.id,'product_id':pcolor,'product_uom_qty':totalesColor,'x_studio_cantidad':str(totalesColor),'price_unit':j.clickExcedenteColor,'name':'(82121500) PAGINAS IMPRESAS COLOR : '+str(totalesColor)+' INCLUYE: '+str(m.bolsaColor)})                                                    
                            self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':j.id,'x_studio_field_9nQhR':k.id,'product_id':pbn,'product_uom_qty':totalesNegro,'x_studio_cantidad':str(totalesNegro),'price_unit':j.clickExcedenteBN,'name':'(82121500) PAGINAS IMPRESAS NEGRO : '+str(totalesNegro)+' INCLUYE: '+str(m.bolsaBN)})                                                                                  
                            self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':j.id,'product_id':rentaG,'product_uom_qty':1.0,'x_studio_cantidad':'1','price_unit':j.rentaMensual,'name':'(80161801) RENTA '+ str(len(p))+' EQUIPOS EN GENERAL.'})                                                                                                                         
               for s in self.x_studio_servicios:
                     if s.nombreAnte=='SERVICIO DE PCOUNTER' or s.nombreAnte=='SERVICIO DE PCOUNTER1' or s.nombreAnte=='ADMINISTRACION DE DOCUMENTOS CON PCOUNTER' or s.nombreAnte=='SERVICIO DE MANTENIMIENTO DE PCOUNTER' or s.nombreAnte=='SERVICIO DE MANTENIMIENTO PCOUNTER' or s.nombreAnte=='RENTA DE LICENCIAMIENTO PCOUNTER':                        
                        self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':s.id,'product_id':spc ,'product_uom_qty':1.0,'x_studio_cantidad':'1','price_unit':s.rentaMensual})                                                                                                    
                     if s.nombreAnte=='SERVICIO DE TFS' or s.nombreAnte=='OPERADOR TFS' or s.nombreAnte=='TFS' or s.nombreAnte=='SERVICIO DE TFS ' :                                                                                                                                                     
                        self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':s.id,'product_id':tfs ,'product_uom_qty':1.0,'x_studio_cantidad':'1','price_unit':s.rentaMensual})                                                            
                        #self.env['account_tax_sale_order_line_rel'].create({'sale_order_line_id': acci.id,'account_tax_id':idtax.id})                                                                                    
                        #self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':s.id,'product_id':11419 ,'product_uom_qty':1.0,'price_unit':s.rentaMensual,'discount':int(self.x_studio_descuento)})                                                                                                    
                     if s.nombreAnte=='SERVICIO DE MANTENIMIENTO':                        
                        self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':s.id,'product_id':sm ,'product_uom_qty':1.0,'x_studio_cantidad':'1','price_unit':s.rentaMensual})                                                                                                    
                     if s.nombreAnte=='LECTORES DE PROXIMIDAD':                        
                        self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':s.id,'product_id':lp ,'product_uom_qty':1.0,'x_studio_cantidad':'1','price_unit':s.rentaMensual})                                                                                                       
                     if s.nombreAnte=='PAPEL 350,000 HOJAS':                        
                        self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':s.id,'product_id':impre ,'product_uom_qty':1.0,'x_studio_cantidad':'1','price_unit':s.rentaMensual})                                                                                                          
                     if s.nombreAnte=='SOPORTE Y MANTENIMIENTO DE EQUIPOS':                        
                        self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':s.id,'product_id':sme ,'product_uom_qty':1.0,'x_studio_cantidad':'1','price_unit':s.rentaMensual})                                                                                                       
                     if s.nombreAnte=='SERVICIO DE ADMINISTRADOR KM NET MANAGER':                        
                        self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':s.id,'product_id':netMa ,'product_uom_qty':1.0,'x_studio_cantidad':'1','price_unit':s.rentaMensual})                                                                                                    
                     if s.nombreAnte=='PAGINAS IMPRESAS EN BN':                        
                        self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':s.id,'product_id':paginasbn ,'product_uom_qty':int(s.cantidad),'x_studio_cantidad':str(int(s.cantidad)),'price_unit':s.rentaMensual})                                                                                                    
                     if s.nombreAnte=='RENTA MENSUAL DE LICENCIA  7 EMBEDED' or s.nombreAnte=='RENTA MENSUAL DE LICENCIA  14 EMBEDED' or  s.nombreAnte=='RENTA MENSUAL DE LICENCIA  2 EMBEDED':                        
                        self.env['sale.order.line'].create({'order_id': sale.id,'x_studio_servicio':s.id,'product_id':embeded ,'product_uom_qty':1.0,'x_studio_cantidad':'1','price_unit':s.rentaMensual})                                                                                                    
                              
      detalle =  fields.One2many('sale.order.detalle', 'saleOrder', string='Order Lines')
                 
class detalle(models.Model):
      _name = 'sale.order.detalle'
      _description = 'Detalle Orden'
     
      saleOrder = fields.Many2one('sale.order', string='Pedido de venta')
      accountInvoice = fields.Many2one('account.invoice', string='Factura')
     
      serieEquipo = fields.Text(string="Serie")
      producto = fields.Text(string="Producto")
      locacion = fields.Text(string="Locación")
      ubicacion = fields.Text(string="ubicación")
     
      ultimaLecturaBN = fields.Integer(string='Última lectura monocromatico')
      lecturaAnteriorBN = fields.Integer(string='Lectura anterior monocromatico')
      paginasProcesadasBN = fields.Integer(string='Páginas procesadas monocromatico')
     
      ultimaLecturaColor = fields.Integer(string='última lectura color')
      lecturaAnteriorColor = fields.Integer(string='Lectura anterior color')
      paginasProcesadasColor = fields.Integer(string='Páginas procesadas color')
     
      periodo = fields.Text(string="Periodo")
      servicio=fields.Integer(string='Servicio')
      estado=   fields.Text(string="Estado")
      color=fields.Text(string="Color")
     
     
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
                                                         , 'producto': h.product_id.name
                                                         , 'serieEquipo': h.name
                                                         
                                                         , 'ultimaLecturaBN': h.x_studio_ultimalecturam
                                                         , 'lecturaAnteriorBN': h.x_studio_lec_ant_bn
                                                         , 'paginasProcesadasBN': h.x_studio_pg_proc
                                                         
                                                         , 'ultimaLecturaColor': h.x_studio_ultimalecturacolor
                                                         , 'lecturaAnteriorColor': h.x_studio_lec_ant_color
                                                         , 'paginasProcesadasColor': h.x_studio_pg_proc_color
                                                        })
# class saleOrderTemp(models.Model):
#   _name='sale.order.temp'
#   _description='lineas temporales para solicitud'
#   serie=fields.Many2one('stock.production.lot')
#   product_id=fields.Many2one('producto.producto','Producto')
#   cantidad=fields.Integer('Cantidad',default=1)
#   toner=fields.Many2many('producto.producto','Toner')
#   accesorios=fields.Many2many('producto.producto','Accesorios')
#   estado=fields.Selection([["Obsoleto","Obsoleto"],["Usado","Usado"],["Hueso","Hueso"],["Para reparación","Para reparación"],["Nuevo","Nuevo"],["Buenas condiciones","Buenas condiciones"],["Excelentes condiciones","Excelentes condiciones"],["Back-up","Back-up"],["Dañado","Dañado"]],'Estado')
#   servicio=fields.Integer()
#   cliente=fields.Char()
#   tipo=fields.Char()

#   @api.onchange('product_id')
#   def domini(self):
#     res={}
#     res['domain']={'accesorios':[('id','in',self.product_id.x_studio_toner_compatible.filtered(lambda x:x.categ_id.id==11).mapped('id'))],'toner':[('id','in',self.product_id.x_studio_toner_compatible.filtered(lambda x:x.categ_id.id==5).mapped('id'))]}
#     return res

#   @api.onchange('tipo'):
#   def ser(self):
#     res={}
#     if(self.tipo=='Retiro'):
#       serv=self.env['servicios'].browser(self.servicio).series.mapped('id')
#       res['domain']={'serie':[('id','in',serv)]}
#     return res

#   @api.onchange('serie')
#   def seri(self):
#     self.product_id=serie.product_id.id
