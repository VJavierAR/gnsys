# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64,io,csv
import logging, ast
import pytz
from odoo.exceptions import UserError
from odoo import exceptions, _
from datetime import datetime
from operator import concat
_logger = logging.getLogger(__name__)




def get_years():
    year_list = []
    for i in range(2010, 2036):
       year_list.append((i, str(i)))
    return year_list
valores = [('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'), ('04', 'Abril'),
                          ('05', 'Mayo'), ('06', 'Junio'), ('07', 'Julio'), ('08', 'Agosto'),
                          ('09', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')]


class dcas(models.Model):
    _name = 'dcas.dcas'
    _description ='DCAS'
    _inherit = ['mail.thread', 'mail.activity.mixin']    
    name = fields.Char()
    dispositivo = fields.Char()
    ultimoInforme=fields.Datetime('Ultimo Informe')
    respaldo=fields.Boolean(string='Respaldo')
    usb=fields.Boolean(string='Usb')
    serie_aux=fields.Char()
    serie=fields.Many2one('stock.production.lot',string='Numero de Serie')
    grupo_aux=fields.Char()
    grupo=fields.Many2one('res.partner',store=True)
    ubicacion=fields.Char()
    ip=fields.Char(string='IP')
    contadorColor=fields.Integer(string='Contador Color')
    contadorMono=fields.Integer(string='Contador Monocromatico')
    contador_id=fields.Many2one('contadores.contadores')        
    dominio=fields.Integer()
    porcentajeNegro=fields.Integer(string='Negro')
    porcentajeAmarillo=fields.Integer(string='Amarillo')
    porcentajeCian=fields.Integer(string='Cian')
    porcentajeMagenta=fields.Integer(string='Magenta')
    fuente=fields.Selection(selection=[('dcas.dcas', 'DCA'),('helpdesk.ticket', 'Mesa'),('stock.production.lot','Equipo'),('tfs.tfs','Tfs')], default='dcas.dcas')  
    cartuchoNegro=fields.Selection([('a', 'Ninguna serie selecionada')], string='prueba')
    nivelNA=fields.Integer(string='Nivel de toner negro anteior')
    nivelAA=fields.Integer(string='Nivel de toner Amarillo anteior')
    nivelCA=fields.Integer(string='Nivel de toner Cian anteior')
    nivelMA=fields.Integer(string='Nivel de toner Magenta anteior')
    contadorAnteriorCian=fields.Integer(string='contador de ultima solicitud Cian')
    contadorAnteriorAmarillo=fields.Integer(string='contador de ultima solicitud Amarillo')
    contadorAnteriorMagenta=fields.Integer(string='contador de ultima solicitud Magenta')
    contadorAnteriorNegro=fields.Integer(string='contador de ultima solicitud Negro')
    contadorAnteriorColor=fields.Integer(string='contador de ultima solicitud Color')
    paginasProcesadasBN=fields.Integer(string='Páginas procesadas BN')
    paginasProcesadasC=fields.Integer(string='Páginas procesadas Cian')
    paginasProcesadasA=fields.Integer(string='Páginas procesadas Amarillo')
    paginasProcesadasM=fields.Integer(string='Páginas procesadas Magenta')
    x_studio_fecha = fields.Datetime(string='Fecha',default=lambda self: fields.datetime.now(pytz.timezone('America/Mexico_City')))
    renC=fields.Float(string='Rendimiento Cian')
    renA=fields.Float(string='Rendimiento Amarillo')
    renM=fields.Float(string='Rendimiento Magenta')
    renN=fields.Float(string='Rendimiento Negro ')
    
    tablahtml=fields.Text(string='Detalle Equipo')
    fechaN=fields.Datetime(string='Fecha de captura')
    fechaA=fields.Datetime(string='Fecha de captura')
    fechaC=fields.Datetime(string='Fecha de captura')
    fechaM=fields.Datetime(string='Fecha de captura')
    tN=fields.Char(string='Ticket BN')
    tA=fields.Char(string='Ticket Amarillo')
    tC=fields.Char(string='Ticket Cian')
    tM=fields.Char(string='Ticket Magenta')
    colorEquipo=fields.Char(string='Color o Bn')
    equipo=fields.Char(string='Equipo')
    ultimaUbicacion=fields.Char(string='Ultima ubicación')
    
    
    

    
    
    
    @api.model
    def create(self, values):               
        _logger.info("values "+str(values))
        c = super(dcas, self).create(values)
        
        _logger.info("c inicio"+str(c.tablahtml))
        _logger.info("self inicio id"+str(c.id))
        """
        contaC=c.contadorColor                       
        cac=c.contadorAnteriorColor
        contadorM=c.contadorMono
        c.paginasProcesadasC=contaC-c.contadorAnteriorCian
        c.paginasProcesadasA=contaC-c.contadorAnteriorAmarillo
        c.paginasProcesadasM=contaC-c.contadorAnteriorMagenta
        c.paginasProcesadasBN=contadorM-c.contadorAnteriorNegro            
        cc=c.x_studio_rendimientoc
        a=c.x_studio_rendimientoa
        m=c.x_studio_rendimientom
        n=c.x_studio_rendimiento_negro
        if cc == '0':
           cc = 1
        if a == '0':
           a = 1
        if m == '0':
           m = 1                        
        if n == '0':
           n = 1                           
        if n:
           c.renN=round(c.paginasProcesadasBN*100/int(n),2)            
        if cc:
           c.renC=round(c.paginasProcesadasC*100/int(cc),2)
        if a:
           c.renA=round(c.paginasProcesadasA*100/int(a),2)
        if m:
           c.renM=round(c.paginasProcesadasM*100/int(m),2)
           
        if c.serie:
           style="<html><head><style>table, th, td {border: 1px solid black;border-collapse: collapse;}th, td {padding: 5px;text-align: left;}</style></head><body>"           
           cabecera="<table ><tr><th></th><th>Monocormatico  </th><th> Cian </th><th> Amarillo </th><th> Magenta </th></tr><tr><tr><td></td></tr>"
           ticket='<tr><td> Ticket </td><td>'+str(c.tN)+'</br>'+'</td> <td>'+str(c.tC)+' </br> </td> <td>'+' '+str(c.tA)+'</br> </td> <td>'+str(c.tM)+'</br> </td> </tr>'
           ultimosContadores='<tr><td> Último Contador </td><td>'+str(c.contadorAnteriorNegro)+'</br>'+'</td> <td>'+str(c.contadorAnteriorCian)+' </br> </td> <td>'+ str(c.contadorAnteriorAmarillo)+'</br> </td> <td>'+str(c.contadorAnteriorMagenta)+' </br> </td> </tr>'
           fechas='<tr><td> Fecha </td><td>'+str(c.fechaN)+'</br>'+'</td> <td>'+str(c.fechaC)+' </br> </td> <td>'+' '+str(c.fechaA)+'</br> </td> <td>'+str(c.fechaM)+'</br> </td> </tr>'
           paginasProcesadas='<tr><td> Páginas Procesadas </td> <td>'+str(c.paginasProcesadasBN)+'</td> <td>'+str(c.paginasProcesadasC)+'</td> <td>'+ str(c.paginasProcesadasA)+' </td> <td>'+str(c.paginasProcesadasM)+'</td></tr>'        
           rendimientos='<tr><td> Rendimiento </td> <td>'+str(c.renN)+'</td> <td>'+str(c.renC)+'</td> <td>'+ str(c.renA)+' </td> <td>'+str(c.renM)+'</td></tr>'
           niveles='<tr><td> Último nivel </td> <td>'+str(c.nivelNA)+'</td> <td>'+str(c.nivelCA)+'</td> <td>'+ str(c.nivelAA)+' </td> <td>'+str(c.nivelMA)+'</td></tr>'           
           cierre="</table></body></html> "
           c.tablahtml=cabecera+ticket+ultimosContadores+fechas+paginasProcesadas+rendimientos+niveles+cierre
           _logger.info("self final antes  "+str(self.tablahtml)) 
           self.env.cr.execute("update dcas_dcas set x_studio_ultima_ubicacin = '"+str(c.x_studio_ultima_ubicacin)+"' where  id = " + str(c.id) + ";")
           _logger.info("c color"+str(c.x_studio_color_o_bn)) 
           _logger.info("c negro anterior"+str(c.contadorAnteriorNegro))
           _logger.info("self negro anterior"+str(self.contadorAnteriorNegro))
           self.env.cr.execute("update dcas_dcas set x_studio_color_o_bn = '"+str(c.x_studio_color_o_bn)+"' where  id = " + str(c.id) + ";")           
           self.env.cr.execute("update dcas_dcas set tablahtml = '"+c.tablahtml+"' where  id = " + str(c.id) + ";")
           _logger.info("c final"+str(c.tablahtml))
           _logger.info("self final "+str(self.tablahtml))
        """
        return c
    
    
    
    
   
    
    @api.onchange('serie')             
    def ultimosContadoresNACM(self):

        
        if self.serie :
            bn_c=self.env['stock.production.lot'].search([['id','=',self.serie.id]])        
            self.colorEquipo=bn_c.x_studio_color_bn
            self.ultimaUbicacion=bn_c.x_studio_ultima_ubicacin
            self.equipo=bn_c.product_id.name
            n=self.env['dcas.dcas'].search([['serie','=',self.serie.id],['porcentajeNegro','=',1]],order='x_studio_fecha desc',limit=1)
            self.fechaN=n.x_studio_fecha
            self.nivelNA=n.x_studio_toner_negro
            self.contadorAnteriorNegro=n.contadorMono
            self.tN=n.x_studio_tickett
            c=self.env['dcas.dcas'].search([['serie','=',self.serie.id],['porcentajeCian','=',1]],order='x_studio_fecha desc',limit=1)
            self.nivelCA=c.x_studio_toner_cian
            self.contadorAnteriorCian=c.contadorColor
            self.fechaC=c.x_studio_fecha
            self.tC=c.x_studio_tickett
            a=self.env['dcas.dcas'].search([['serie','=',self.serie.id],['porcentajeAmarillo','=',1]],order='x_studio_fecha desc',limit=1)
            self.nivelAA=a.x_studio_toner_amarillo
            self.contadorAnteriorAmarillo=a.contadorColor
            self.fechaA=a.x_studio_fecha
            self.tA=a.x_studio_tickett
            m=self.env['dcas.dcas'].search([['serie','=',self.serie.id],['porcentajeMagenta','=',1]],order='x_studio_fecha desc',limit=1)
            self.nivelMA=m.x_studio_toner_magenta
            self.contadorAnteriorMagenta=m.contadorColor
            self.fechaM=m.x_studio_fecha
            self.tM=m.x_studio_tickett
            #select "contadorColor" from dcas_dcas where "porcentajeMagenta"=1 or "porcentajeCian"=1 or "porcentajeNegro"=1  order by x_studio_fecha desc limit 1;
            query="select \"contadorColor\" from dcas_dcas where  serie="+str(self.serie.id)+" or \"porcentajeMagenta\"=1 or \"porcentajeCian\"=1 or \"porcentajeMagenta\"=1  order by x_studio_fecha desc limit 1;"                        
            self.env.cr.execute(query)                        
            informacion = self.env.cr.fetchall()
            #raise  exceptions.ValidationError(str(informacion)+' '+ str(type(informacion))+' '+str(informacion[0]) +' el chido xD'+str(informacion[0][0]))
            self.contadorAnteriorColor = informacion[0][0]
        if self.serie:
            style="<html><head><style>table, th, td {border: 1px solid black;border-collapse: collapse;}th, td {padding: 5px;text-align: left;}</style></head><body>"
            cabecera="<table style='width:100%'><tr><th></th><th>Monocormatico  </th><th> Cian </th><th> Amarillo </th><th> Magenta </th></tr><tr><tr><td></td></tr>"
            ticket='<tr><td> Ticket </td><td>'+str(self.tN)+'</br>'+'</td> <td>'+str(self.tC)+' </br> </td> <td>'+' '+str(self.tA)+'</br> </td> <td>'+str(self.tM)+'</br> </td> </tr>'
            ultimosContadores='<tr><td> Último Contador </td><td>'+str(self.contadorAnteriorNegro)+'</br>'+'</td> <td>'+str(self.contadorAnteriorCian)+' </br> </td> <td>'+ str(self.contadorAnteriorAmarillo)+'</br> </td> <td>'+str(self.contadorAnteriorMagenta)+' </br> </td> </tr>'
            fechas='<tr><td> Fecha </td><td>'+str(self.fechaN)+'</br>'+'</td> <td>'+str(self.fechaC)+' </br> </td> <td>'+' '+str(self.fechaA)+'</br> </td> <td>'+str(self.fechaM)+'</br> </td> </tr>'
            paginasProcesadas='<tr><td> Páginas Procesadas </td> <td>'+str(self.paginasProcesadasBN)+'</td> <td>'+str(self.paginasProcesadasC)+'</td> <td>'+ str(self.paginasProcesadasA)+' </td> <td>'+str(self.paginasProcesadasM)+'</td></tr>'        
            rendimientos='<tr><td> Rendimiento </td> <td>'+str(self.renN)+'</td> <td>'+str(self.renC)+'</td> <td>'+ str(self.renA)+' </td> <td>'+str(self.renM)+'</td></tr>'
            niveles='<tr><td> Último nivel </td> <td>'+str(self.nivelNA)+'</td> <td>'+str(self.nivelCA)+'</td> <td>'+ str(self.nivelAA)+' </td> <td>'+str(self.nivelMA)+'</td></tr>'
            cartuchos='<tr><td> Cartuchos Selecionados </td> <td>'+str(self.x_studio_cartuchonefro.name)+'</td> <td>'+str(self.x_studio_cartucho_cian_1.name)+'</td> <td>'+ str(self.x_studio_cartucho_amarillo.name)+' </td> <td>'+str(self.x_studio_cartucho_magenta.name)+'</td></tr>'
            cierre="</table></body></html> "
            self.tablahtml=cabecera+ticket+ultimosContadores+fechas+paginasProcesadas+rendimientos+niveles+cartuchos+cierre    
            #query = "update dcas_dcas set tablahtml = \""+cabecera+ticket+ultimosContadores+fechas+paginasProcesadas+rendimientos+niveles+cierre+"\" where id = " + str(self.id) + ";"
            #ss = self.env.cr.execute(query)
    
    @api.onchange('contadorMono')
    def validaMoon(self):        
        contadorM=self.contadorMono
        cam=self.contadorAnteriorNegro                                        
        if cam>contadorM:            
            raise exceptions.ValidationError("Contador Monocromatico Menor")

            


    @api.onchange('x_studio_cartuchonefro','x_studio_cartucho_amarillo','x_studio_cartucho_cian_1','x_studio_cartucho_magenta')
    def vcalcula(self):
        contaC=self.contadorColor                       
        cac=self.contadorAnteriorColor
        contadorM=self.contadorMono
        self.paginasProcesadasC=contaC-self.contadorAnteriorCian
        self.paginasProcesadasA=contaC-self.contadorAnteriorAmarillo
        self.paginasProcesadasM=contaC-self.contadorAnteriorMagenta
        self.paginasProcesadasBN=contadorM-self.contadorAnteriorNegro            
        c=self.x_studio_rendimientoc
        a=self.x_studio_rendimientoa
        m=self.x_studio_rendimientom
        n=self.x_studio_rendimiento_negro
        if c == '0':
           c = 1
        if a == '0':
           a = 1
        if m == '0':
           m = 1                        
        if n == '0':
           n = 1                   
        if n:
           self.renN=round(self.paginasProcesadasBN*100/int(n),2)            
        if c:
           self.renC=round(self.paginasProcesadasC*100/int(c),2)
        if a:
           self.renA=round(self.paginasProcesadasA*100/int(a),2)
        if m:
           self.renM=round(self.paginasProcesadasM*100/int(m),2)
        if self.serie:
           style="<html><head><style>table, th, td {border: 1px solid black;border-collapse: collapse;}th, td {padding: 5px;text-align: left;}</style></head><body>"
           cabecera="<table style='width:100%'><tr><th></th><th>Monocormatico  </th><th> Cian </th><th> Amarillo </th><th> Magenta </th></tr><tr><tr><td></td></tr>"
           ticket='<tr><td> Ticket </td><td>'+str(self.tN)+'</br>'+'</td> <td>'+str(self.tC)+' </br> </td> <td>'+' '+str(self.tA)+'</br> </td> <td>'+str(self.tM)+'</br> </td> </tr>'
           ultimosContadores='<tr><td> Último Contador </td><td>'+str(self.contadorAnteriorNegro)+'</br>'+'</td> <td>'+str(self.contadorAnteriorCian)+' </br> </td> <td>'+ str(self.contadorAnteriorAmarillo)+'</br> </td> <td>'+str(self.contadorAnteriorMagenta)+' </br> </td> </tr>'
           fechas='<tr><td> Fecha </td><td>'+str(self.fechaN)+'</br>'+'</td> <td>'+str(self.fechaC)+' </br> </td> <td>'+' '+str(self.fechaA)+'</br> </td> <td>'+str(self.fechaM)+'</br> </td> </tr>'
           paginasProcesadas='<tr><td> Páginas Procesadas </td> <td>'+str(self.paginasProcesadasBN)+'</td> <td>'+str(self.paginasProcesadasC)+'</td> <td>'+ str(self.paginasProcesadasA)+' </td> <td>'+str(self.paginasProcesadasM)+'</td></tr>'        
           rendimientos='<tr><td> Rendimiento </td> <td>'+str(self.renN)+'</td> <td>'+str(self.renC)+'</td> <td>'+ str(self.renA)+' </td> <td>'+str(self.renM)+'</td></tr>'
           niveles='<tr><td> Último nivel </td> <td>'+str(self.nivelNA)+'</td> <td>'+str(self.nivelCA)+'</td> <td>'+ str(self.nivelAA)+' </td> <td>'+str(self.nivelMA)+'</td></tr>'
           cartuchos='<tr><td> Cartuchos Selecionados </td> <td>'+str(self.x_studio_cartuchonefro.name)+'</td> <td>'+str(self.x_studio_cartucho_cian_1.name)+'</td> <td>'+ str(self.x_studio_cartucho_amarillo.name)+' </td> <td>'+str(self.x_studio_cartucho_magenta.name)+'</td></tr>'
           cierre="</table></body></html> "
           self.tablahtml=cabecera+ticket+ultimosContadores+fechas+paginasProcesadas+rendimientos+niveles+cartuchos+cierre
        
                    
                
            
    @api.onchange('contadorColor')
    def validaContadores(self):
        contaC=self.contadorColor                       
        cac=self.contadorAnteriorColor
        contadorM=self.contadorMono
        if cac>contaC:            
            raise exceptions.ValidationError("Contador Color Menor.")
            
    
    """
    @api.onchange('contadorColor','contadorMono','x_studio_cartuchonefro','x_studio_cartucho_amarillo','x_studio_cartucho_cian_1','x_studio_cartucho_magenta')
    def table(self):
        if self.serie:
            style="<html><head><style>table, th, td {border: 1px solid black;border-collapse: collapse;}th, td {padding: 5px;text-align: left;}</style></head><body>"
            cabecera="<table style='width:100%'><caption>Info xD</caption><tr><th></th><th>Monocormatico  </th><th> Cian </th><th> Amarillo </th><th> Magenta </th></tr><tr><tr><td></td></tr>"
            ticket='<tr><td> Ticket </td><td>'+str(self.tN)+'</br>'+'</td> <td>'+str(self.tC)+' </br> </td> <td>'+' '+str(self.tA)+'</br> </td> <td>'+str(self.tM)+'</br> </td> </tr>'
            ultimosContadores='<tr><td> Último Contador </td><td>'+str(self.contadorAnteriorNegro)+'</br>'+'</td> <td>'+str(self.contadorAnteriorCian)+' </br> </td> <td>'+ str(self.contadorAnteriorAmarillo)+'</br> </td> <td>'+str(self.contadorAnteriorMagenta)+' </br> </td> </tr>'
            fechas='<tr><td> Fecha </td><td>'+str(self.fechaN)+'</br>'+'</td> <td>'+str(self.fechaC)+' </br> </td> <td>'+' '+str(self.fechaA)+'</br> </td> <td>'+str(self.fechaM)+'</br> </td> </tr>'
            paginasProcesadas='<tr><td> Páginas Procesadas </td> <td>'+str(self.paginasProcesadasBN)+'</td> <td>'+str(self.paginasProcesadasC)+'</td> <td>'+ str(self.paginasProcesadasA)+' </td> <td>'+str(self.paginasProcesadasM)+'</td></tr>'        
            rendimientos='<tr><td> Rendimiento </td> <td>'+str(self.renN)+'</td> <td>'+str(self.renC)+'</td> <td>'+ str(self.renA)+' </td> <td>'+str(self.renM)+'</td></tr>'
            niveles='<tr><td> Último nivel </td> <td>'+str(self.nivelNA)+'</td> <td>'+str(self.nivelCA)+'</td> <td>'+ str(self.nivelAA)+' </td> <td>'+str(self.nivelMA)+'</td></tr>'
            cierre="</table></body></html> "
            self.tablahtml=cabecera+ticket+ultimosContadores+fechas+paginasProcesadas+rendimientos+niveles+cierre                                                                                                                                                                                 
    """
    
    

    

class contadores(models.Model):
    _name = 'contadores.contadores'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Contadores Cliente'
    name = fields.Char()
    mes=fields.Selection(valores,string='Mes')
    anio= fields.Selection(get_years(), string='Año')
    
    dca = fields.One2many('dcas.dcas',inverse_name='contador_id',string='DCAS')
    cliente = fields.Many2one('res.partner', store=True,string='Cliente')
    localidad=fields.Many2one('res.partner',store='True',string='Localidad')
    archivo=fields.Binary(store='True',string='Archivo')
    estado=fields.Selection(selection=[('Abierto', 'Abierto'),('Incompleto', 'Incompleto'),('Valido','Valido')],widget="statusbar", default='Abierto')  
    dom=fields.Char(readonly="1",invisible="1")
    order_line = fields.One2many('contadores.lines','ticket',string='Order Lines')
    

    
    #@api.onchange('serie_aux')
    def getid(self):
        self.serie=self.env['stock.production.lot'].search([['name','=',self.serie_aux]]).id
        
    
    @api.multi
    def carga_contadores_fac(self):
        if self.x_studio_estado_capturas=='Listo':
            for r in self.detalle:
                rr=self.env['dcas.dcas'].create({'serie': r.producto
                                                 ,'contadorColor':r.ultimaLecturaColor
                                                 ,'contadorMono':r.ultimaLecturaBN
                                                 ,'fuente':'dcas.dcas'
                                                 ,'x_studio_field_no6Rb':str(self.anio)+'-'+str(self.mes)
                                                 ,'x_studio_fecha_texto_anio':str(valores[int(self.mes[1])-1][1])+' de '+str(self.anio)
                                                })                    
    
    #@api.onchange('mes')
    @api.multi
    def carga_contadores(self):
        if self.anio:
            perido=str(self.anio)+'-'+str(self.mes)
            periodoAnterior=''
            mesA=''
            anioA=''
            i=0
            for f in valores:                
                if f[0]==str(self.mes):                
                   mesaA=str(valores[i-1][0])
                i=i+1
            anios=get_years()
            i=0
            for e in anios:
                if e[0]==int(self.anio) and str(self.mes)=='01':
                   anioA=str(anios[i-1][0])
                else:
                   anioA=str(self.anio)                
                i=i+1                
            periodoAnterior= anioA+'-'+mesaA   
            
            asd=self.env['stock.production.lot'].search([('x_studio_ubicaciontest','=',self.cliente.name)])
            #raise Warning('notihng to show xD '+str(self.cliente.name))
            #id=int(self.id)            
            sc=self.env['contadores.contadores'].search([('id', '=', self.id)])
            sc.write({'name' : str(self.cliente.name)+' '+str(periodoAnterior)+' a '+str(perido)})
            for a in asd:
                currentP=self.env['dcas.dcas'].search([('serie','=',a.id),('x_studio_field_no6Rb', '=', perido)])
                currentPA=self.env['dcas.dcas'].search([('serie','=',a.id),('x_studio_field_no6Rb', '=', periodoAnterior)])
                #raise exceptions.ValidationError("q onda xd"+str(self.id)+' id  '+str(id))                     
                rr=self.env['contadores.contadores.detalle'].create({'contadores': self.id
                                                       ,'producto': a.id
                                                       ,'serieEquipo': a.name
                                                       #,'locacion':currentP.x_studio_locacion_recortada
                                                       ,  'periodo':perido                                                              
                                                       , 'ultimaLecturaBN': currentP.contadorMono
                                                       , 'lecturaAnteriorBN': currentPA.contadorMono
                                                       #, 'paginasProcesadasBN': bnp                                                   
                                                       ,  'periodoA':periodoAnterior            
                                                       , 'ultimaLecturaColor': currentP.contadorColor
                                                       , 'lecturaAnteriorColor': currentPA.contadorColor                                                             
                                                       #, 'paginasProcesadasColor': colorp
                                                       , 'bnColor':a.x_studio_color_bn              
                                                       })
                #rr.write({'contadores':id})
            
        
            
            


    #@api.onchange('archivo')
    def onchange_archiv(self):
        f=open('1.txt','w')
        for record in self:
            if record.archivo:
                s=base64.b64decode(record.archivo)
                cv1=io.StringIO(str(s))
                #writer = csv.writer(cv1, dialect='excel', delimiter=',')
                split=str(s).split('\\n')
                #split=str(s).split('\n')
                i=0
                for sp in split:
                    if(i>0):
                        dat=sp.split(' - ',1)
                        campos=dat[1].split(',')
                        p=self.env['res.partner'].search([['name','=',dat[0]]])
                        h=self.env['res.partner'].search([['name','=',campos[0]],['parent_id','=',p.id]])
                        t=self.env['stock.production.lot'].search([['name','=',campos[3]]])
                        f.write(str(len(t))+'\n')
                    i=i+1
        f.close()
                        #record.dca.search([['serial.name','=',dat[3]]])

    detalle =  fields.One2many('contadores.contadores.detalle', 'contadores', string='Contadores')
   

    
class detalleContadores(models.Model):
      _name = 'contadores.contadores.detalle'
      _description = 'Detalle Contadores'
     
      contadores = fields.Many2one('contadores.contadores', string='Detalle de contadores')
     
      serieEquipo = fields.Text(string="Serie")
      producto = fields.Text(string="Producto")
      locacion = fields.Text(string="Locación")
      capturar = fields.Boolean()     
      bnColor = fields.Text(string='Equipo B/N o Color')  
      ultimaLecturaBN = fields.Integer(string='Última lectura monocromatico')
      lecturaAnteriorBN = fields.Integer(string='Lectura anterior monocromatico')
      paginasProcesadasBN = fields.Integer(string='Páginas procesadas monocromatico')
    
     
      ultimaLecturaColor = fields.Integer(string='última lectura color')
      lecturaAnteriorColor = fields.Integer(string='Lectura anterior color')
      paginasProcesadasColor = fields.Integer(string='Páginas procesadas color')
     
      periodo = fields.Text(string="Periodo")
      periodoA = fields.Text(string="Periodo Anterior")
      archivo=fields.Binary(store='True',string='Archivo')
   

    
    
    
class contadores_lines(models.Model):
    _name="contadores.lines"
    _description = "lineas contadores"
    serie=fields.Many2one('stock.production.lot')
    ticket=fields.Many2one('contadores.contadores',string='Order Reference')
    contadorAnterior=fields.Many2one('dcas.dcas',string='Anterior',compute='ultimoContador')
    contadorColor=fields.Integer(string='Contador Color')
    contadorNegro=fields.Integer(string='Contador Monocromatico')
    contadorAnteriorMono=fields.Integer(related='contadorAnterior.contadorMono',string='Anterior Monocromatico')
    contadorAnteriorColor=fields.Integer(related='contadorAnterior.contadorColor',string='Anterior Color')
    cliente=fields.Many2one('res.partner')
    nombre=fields.Char(related='cliente.name',string='Nombre Cliente')
    mes=fields.Integer()
    pagina=fields.Binary('Pagina de Estado')
    
    #@api.depends('serie')
    def ultimoContador(self):
        fecha=datetime.datetime.now()
        for record in self:
            if(record.serie):
                dc=self.env['dcas.dcas'].search([('fuente','=','dcas.dcas'),('x_studio_fecha_techra','!=',False),('serie','=',record.serie.id)]).sorted(key='x_studio_fecha_techra')
                if(len(dc)>1):
                    record['contadorAnterior']=dc[0].id
        
class lor(models.Model):
    _inherit = 'stock.production.lot'
    dca=fields.One2many('dcas.dcas',inverse_name='serie')

    
    
    
class contadores_lines(models.Model):
    _name="cambios.localidad"
    _description = "Cambios de Localidad"
    estado=fields.Selection(selection=[('1','Por Confirma'),('2','Confirmado')])
    serie=fields.Many2one('stock.production.lot')
    origen=fields.Many2one('res.partner')
    destino=fields.Many2one('res.partner')
    
    @api.onchange('serie')
    def ubicacion(self):
        if(self.serie.x_studio_move_line):
            if(self.serie.x_studio_move_line.location_dest_id.x_studio_field_JoD2k):
                if(self.serie.x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z):
                    self.origen=self.serie.x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.id
                    
    def cambio(self):
        if(self.destino):
            origen2=self.env['stock.warehouse'].search([('x_studio_field_E0H1Z','=',self.origen.id)])
            destino2=self.env['stock.warehouse'].search([('x_studio_field_E0H1Z','=',self.destino.id)])
            self.env['stock.move.line'].create({'product_id':self.serie.product_id.id, 'product_uom_id':1,'location_id':origen2.lot_stock_id.id,'product_uom_qty':1,'lot_id':self.serie.id
                                                ,'date':datetime.datetime.now(),'location_dest_id':destino2.lot_stock_id.id})
            self.serie.x_studio_cambio = not self.serie.x_studio_cambio
            self.estado='2'

            
            
