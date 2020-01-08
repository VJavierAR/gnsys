# -*- coding: utf-8 -*-

from odoo import models, fields, api
import base64,io,csv
import logging, ast
_logger = logging.getLogger(__name__)

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
    mes=fields.Selection(selection=[('1','Enero'),('2','Febrero'),('3','Marzo'),('4','Abril'),('5','Mayo'),('6','Junio'),('7','Julio'),('8','Agosto'),('9','Septiembre'),('10','Octubre'),('11','Noviembre'),('12','Diciembre')])
    dca = fields.One2many('dcas.dcas',inverse_name='contador_id',string='DCAS')
    cliente = fields.Many2one('res.partner', store=True,string='Cliente')
    localidad=fields.Many2one('res.partner',store='True',string='Localidad')
    archivo=fields.Binary(store='True',string='Archivo')
    estado=fields.Selection(selection=[('Abierto', 'Abierto'),('Incompleto', 'Incompleto'),('Valido','Valido')],widget="statusbar", default='Abierto')  
    dom=fields.Char(readonly="1",invisible="1")
    order_line = fields.One2many('contadores.lines','ticket',string='Order Lines')

    
    @api.onchange('serie_aux')
    def getid(self):
        self.serie=self.env['stock.production.lot'].search([['name','=',self.serie_aux]]).id
        
    
    
    @api.onchange('cliente')
    def onchange_place(self):
        self.order_line=[(5,0,0)]
        res = {}
        d=[]
        if(self.cliente):
            lotes=self.env['stock.production.lot'].search([['x_studio_ultima_ubicacin', '=' ,self.cliente.name]])
            _logger.info("Contadores"+str(len(lotes)))
            for l in lotes:
                #if(l.x_studio_ultima_ubicacin == self.cliente.name):
                datos={}
                datos['serie']=l.id
                d.append(datos)            
            self.order_line=d
        #return res
    
    

    @api.onchange('localidad')
    def onchange_localidad(self):
        stock=0
        for record in self:
            quants=[]
            record['dca']=[(5,0,0)]
            if(len(record.localidad)==1):
                stock=self.env['stock.warehouse'].search([['x_studio_field_E0H1Z','=',record.localidad.id]]).lot_stock_id.id
                lotes=self.env['stock.production.lot'].search([['x_studio_ubicacion_id','=',stock]])
                b=[]
                c={}
                for f in lotes:
                    c['serie']=f
                    b.append(c)
                record['dom']=stock
                record['dca']=b

    @api.onchange('archivo')
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

    @api.depends('serie')
    def ultimoContador(self):
        for record in self:
            j=0
            
            for dc in record.serie.dca.search([('fuente','=','dcas.dcas')]):
                if(j==0):
                    record['contadorAnterior']=dc.id
                    j=j+1
    @api.onchange('cliente')
    def pr_filtro(self):
        res = {}
        d=[]
        if self.cliente !='False':
            res['domain']={'serie':[('x_studio_ubicaciontest','ilike',self.cliente.name)]}
        return res
    
    
class lor(models.Model):
    _inherit = 'stock.production.lot'
    dca=fields.One2many('dcas.dcas',inverse_name='serie')
