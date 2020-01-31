# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo import exceptions
class tfs(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']    
    _name = 'tfs.tfs'
    _description='tfs'
    name = fields.Char()
    almacen = fields.Many2one('stock.warehouse', "Almacen",store='True',compute='onchange_localidad')
    tipo = fields.Selection([('cian', 'cian'),('magenta','magenta'),('amarillo','amarillo'),('negro','negro')])
    usuario = fields.Many2one('res.partner')
    inventario = fields.One2many(comodel='stock.quant',related='almacen.lot_stock_id.quant_ids', string="Quants")
    cliente = fields.Many2one('res.partner', store=True,string='Cliente')
    localidad=fields.Many2one('res.partner',store='True',string='Localidad')
    serie=fields.Many2one('stock.production.lot',string='Numero de Serie',store='True')
    domi=fields.Integer()
    producto=fields.Many2one('product.product',string='Toner')
    contadorAnterior=fields.Many2one('dcas.dcas',string='Anterior',compute='ultimoContador')
    contadorAnteriorMono=fields.Integer(related='contadorAnterior.contadorMono',string='Monocromatico')
    contadorAnteriorColor=fields.Integer(related='contadorAnterior.contadorColor',string='Color')
    porcentajeAnteriorNegro=fields.Integer(related='contadorAnterior.porcentajeNegro',string='Negro')
    porcentajeAnteriorCian=fields.Integer(related='contadorAnterior.porcentajeCian',string='Cian')
    porcentajeAnteriorAmarillo=fields.Integer(related='contadorAnterior.porcentajeAmarillo',string='Amarillo')
    porcentajeAnteriorMagenta=fields.Integer(related='contadorAnterior.porcentajeMagenta',string='Magenta')
    actualMonocromatico=fields.Integer(string='Contador Monocromatico')
    actualColor=fields.Integer(string='Contador Color')
    actualporcentajeNegro=fields.Integer(string='Toner Negro %')
    actualporcentajeAmarillo=fields.Integer(string='Toner Amarillo %')
    actualporcentajeCian=fields.Integer(string='Toner Cian %')
    actualporcentajeMagenta=fields.Integer(string='Toner Magenta%')
    evidencias=fields.One2many('tfs.evidencia',string='Evidencias',inverse_name='tfs_id')
    estado=fields.Selection([('borrador','Borrador'),('xValidar','Por Validar'),('Valido','Valido')])
    
    @api.one
    def confirm(self):
        for record in self:
            if(len(record.inventario)>0):
                In=self.inventario.search([['product_id.name','=',self.producto.name]]).sorted(key='quantity',reverse=True)
                #for qua in record.inventario:
                #    qua.product_id.id==self.producto.id
                #    if(qua.product_id.id==self.producto.id):
                if(len(In)>0):
                    if(self.tipo=='negro'):
                        rendimientoMono=self.actualMonocromatico-self.contadorAnteriorMono
                        porcentaje=(100*rendimientoMono)/self.producto.x_studio_rendimiento_toner if self.producto.x_studio_rendimiento_toner>0 else 1
                        if(porcentaje<60):
                            self.write({'estado':'xValidar'})
                        else:
                            self.write({'estado':'Valido'})
                            In.write({'quantity':In[0].quantity-1})
                    else:
                        rendimientoColor=self.actualColor-self.contadorAnteriorColor
                        porcentaje=(100*rendimientoColor)/self.producto.x_studio_rendimiento_toner if self.producto.x_studio_rendimiento_toner>0 else 1
                        if(porcentaje<60):
                            self.write({'estado':'xValidar'})
                        else:
                            self.write({'estado':'Valido'})
                            In.write({'quantity':In[0].quantity-1})
                else:
                    raise exceptions.UserError("No existen cantidades en el almacen para el producto " + self.producto.name)
                
    
    
    
    #@api.onchange('cliente')
    #def onchange_cliente(self):
    #    res = {}
    #    for record in self:
     #       res['domain'] = {'localidad': ['&',('parent_id.id', '=', record.cliente.id),('type', '=', 'delivery')]}
      #      record['usuario']=self.env.user.partner_id.id
      #  return res
    
    #@api.model
    #def create(self, vals):
     #   vals['name'] = self.env['ir.sequence'].next_by_code('tfs')
      #  result = super(tfs, self).create(vals)
       # return result
    
    #@api.onchange('usuario')
    #def onchange_user(self):
    #    res={}
    #    cont=[]
    #    condic=[]
     #   for record in self:
     #       almacenes=self.env['stock.warehouse'].search([['x_studio_tfs','=',record.usuario.id]])
     #       for al in almacenes:
     #           if(al.x_studio_field_E0H1Z.parent_id.id not in cont):
     #               cont.append(('id','=',al.x_studio_field_E0H1Z.parent_id.id))
     #       tot=len(cont)-1
     #       for i in range(tot):
     #           condic.append('|')
     #       condic.extend(cont)
     #       res['domain'] = {'cliente': condic}
     #   return res
    
    @api.depends('producto')
    def onchange_localidad(self):
        res={}
        for record in self:
            if record.localidad:
                record['almacen'] =self.env['stock.warehouse'].search([['x_studio_field_E0H1Z','=',record.localidad.id]]).lot_stock_id.x_studio_almacn_padre
                
    
    @api.depends('almacen')
    def cambio(self):
        res={}
        for record in self:
            if record.almacen:
                record['domi']=0
                #record.almacenlot_stock_id.id
                
                #res['domain'] = {'serie': [('x_studio_ubicacion_id', '=', record.almacen.lot_stock_id.id)]}
        #return res
    @api.multi
    @api.depends('serie')
    def ultimoContador(self):
        i=0
        res={}
        for record in self:
            lista=[]
            if record.serie:
                for toner in record.serie.product_id.x_studio_toner_compatible:
                    if('Toner' in toner.categ_id.name):
                        lista.append(str(toner.id))
                #record['name']=str(lista)
                res['domain'] = {'producto': [('id', 'in', lista)]}
                for move_line in record.serie.x_studio_move_line:
                    if(i==0):
                        cliente = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id
                        localidad=move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.id
                        record['cliente'] = cliente
                        record['localidad'] = localidad
                        i=1
            #if record.localidad:
             #   record['almacen'] =self.env['stock.warehouse'].search([['x_studio_field_E0H1Z','=',record.localidad.id]])
            #self.onchange_localidad()
        return res


class evidencias(models.Model):
    _name='tfs.evidencia'
    _description='tfs evidencia'
    name=fields.Char(string='Descripcion')
    evidencia=fields.Binary(string='Archivo')
    tfs_id=fields.Many2one('tfs.tfs')
