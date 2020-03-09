# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64,io,csv
import logging, ast
from odoo.exceptions import UserError
from odoo import exceptions, _
import datetime
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
                if e[0]==int(self.anio):
                   anioA=str(anios[i-1][0])
                i=i+1                
            periodoAnterior= anioA+'-'+mesaA   
            
            asd=self.env['stock.production.lot'].search([('x_studio_ubicaciontest','=',self.cliente.name)])
            #raise Warning('notihng to show xD '+str(self.cliente.name))
            #id=int(self.id)            
            sc=self.env['contadores.contadores'].search([('id', '=', self.id)])
            sc.write({'name' : str(self.cliente.name)+' '+str(periodo)+' '+str(self.id)})
            for a in asd:
                currentP=self.env['dcas.dcas'].search([('serie','=',a.id),('x_studio_field_no6Rb', '=', perido)])
                currentPA=self.env['dcas.dcas'].search([('serie','=',a.id),('x_studio_field_no6Rb', '=', periodoAnterior)])
                #raise exceptions.ValidationError("q onda xd"+str(self.id)+' id  '+str(id))                     
                rr=self.env['contadores.contadores.detalle'].create({'contadores': self.id
                                                       #,'producto': currentP.product_id.display_name
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

            
            
