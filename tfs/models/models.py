# -*- coding: utf-8 -*-
from collections import namedtuple
import json
import time
from datetime import date

from itertools import groupby
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from operator import itemgetter
from odoo import exceptions
import logging, ast
_logger = logging.getLogger(__name__)

class tfs(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']    
    _name = 'tfs.tfs'
    _description='tfs'
    name = fields.Char()
    almacen = fields.Many2one('stock.warehouse', "Almacen",store='True')
    tipo = fields.Selection([('Cian', 'Cian'),('Magenta','Magenta'),('Amarillo','Amarillo'),('Negro','Negro')])
    usuario = fields.Many2one('res.partner')
    inventario = fields.One2many(comodel='stock.quant',related='almacen.lot_stock_id.quant_ids', string="Quants")
    cliente = fields.Many2one('res.partner', store=True,string='Cliente')
    localidad=fields.Many2one('res.partner',store='True',string='Localidad')
    serie=fields.Many2one('stock.production.lot',string='Numero de Serie',store='True')
    domi=fields.Integer()
    productoNegro=fields.Many2one('product.product',string='Toner Monocromatico')
    productoCian=fields.Many2one('product.product',string='Toner Cian')
    productoMagenta=fields.Many2one('product.product',string='Toner Magenta')
    productoAmarillo=fields.Many2one('product.product',string='Toner Amarillo')

    contadorMono=fields.Many2one('dcas.dcas',string='Anterior Monocromatico',store=True)
    contadorCian=fields.Many2one('dcas.dcas',string='Anterior Cian')
    contadorMagenta=fields.Many2one('dcas.dcas',string='Anterior Magenta')
    contadorAmarillo=fields.Many2one('dcas.dcas',string='Anterior Amarillo')
    
    contadorAnteriorMono=fields.Integer(related='contadorMono.contadorMono',string='Anterior Monocromatico',store=True)
    contadorAnteriorCian=fields.Integer(related='contadorCian.contadorColor',string='Anterior Cian')
    contadorAnteriorMagenta=fields.Integer(related='contadorMagenta.contadorColor',string='Anterior Magenta')
    contadorAnteriorAmarillo=fields.Integer(related='contadorAmarillo.contadorColor',string='Anterior Amarillo')

    porcentajeAnteriorNegro=fields.Integer(related='contadorMono.porcentajeNegro',string='Anterior Monocromatico',store=True)
    porcentajeAnteriorCian=fields.Integer(related='contadorCian.porcentajeCian',string='Anterior Cian',store=True)
    porcentajeAnteriorAmarillo=fields.Integer(related='contadorAmarillo.porcentajeAmarillo',string='Anterior Amarillo',store=True)
    porcentajeAnteriorMagenta=fields.Integer(related='contadorMagenta.porcentajeMagenta',string='Anterior Magenta',store=True)
    
    actualMonocromatico=fields.Integer(string='Contador Monocromatico')
    actualColor=fields.Integer(string='Contador Color')
    
    actualporcentajeNegro=fields.Integer(string='Actual Monocromatico')
    actualporcentajeAmarillo=fields.Integer(string='Actual Amarillo')
    actualporcentajeCian=fields.Integer(string='Actual Cian ')
    actualporcentajeMagenta=fields.Integer(string='Actual Magenta')
    
    evidencias=fields.One2many('tfs.evidencia',string='Evidencias',inverse_name='tfs_id')
    estado=fields.Selection([('borrador','Borrador'),('xValidar','Por Validar'),('Valido','Valido'),('Confirmado','Confirmado')])

    colorBN=fields.Selection(related='serie.x_studio_color_bn')
    
    @api.multi
    def confirm(self):
        for record in self:
            if(len(record.evidencias)==0):
                raise exceptions.UserError("No hay evidencias registradas")                
            if(len(record.inventario)>0):
                In=self.inventario.search([['product_id.name','=',self.producto.name],['location_id','=',self.almacen.lot_stock_id.id]]).sorted(key='quantity',reverse=True)
                #for qua in record.inventario:
                #    qua.product_id.id==self.producto.id
                #    if(qua.product_id.id==self.producto.id):
                if(len(In)>0 and In[0].quantity>0):
                    if(self.tipo=='Negro'):
                        rendimientoMono=self.actualMonocromatico-self.contadorAnteriorMono
                        porcentaje=(100*rendimientoMono)/self.producto.x_studio_rendimiento_toner if self.producto.x_studio_rendimiento_toner>0 else 1
                        _logger.info('porcentaje'+str(porcentaje))
                        self.actualporcentajeNegro=porcentaje
                        if(porcentaje<60):
                            self.write({'estado':'xValidar'})
                        else:
                            self.write({'estado':'Valido'})
                            self.env['dcas.dcas'].create({'x_studio_toner_'+str(self.tipo).lower():1,'serie':record.serie.id,'contadorMono':record.actualMonocromatico,'contadorColor':record.actualColor,'fuente':'tfs.tfs','porcentajeMagenta':self.actualporcentajeMagenta,'porcentajeNegro':self.actualporcentajeNegro,'porcentajeAmarillo':self.actualporcentajeAmarillo,'porcentajeCian':self.actualporcentajeCian})
                            #In[0].write({'quantity':In[0].quantity-1})
                    else:
                        rendimientoColor=self.actualColor-self.contadorAnteriorColor
                        porcentaje=(100*rendimientoColor)/self.producto.x_studio_rendimiento_toner if self.producto.x_studio_rendimiento_toner>0 else 1
                        
                        self.write({'actualporcentaje'+str(self.Tipo):porcentaje})
                        if(porcentaje<60):
                            self.write({'estado':'xValidar'})
                        else:
                            self.write({'estado':'Valido'})
                            #_logger.info(In[0])
                            #In[0].write({'quantity':In[0].quantity-1})
                            self.env['dcas.dcas'].create({'x_studio_toner_'+str(self.tipo).lower():1,'serie':record.serie.id,'contadorMono':record.actualMonocromatico,'contadorColor':record.actualColor,'fuente':'tfs.tfs','porcentajeMagenta':self.actualporcentajeMagenta,'porcentajeNegro':self.actualporcentajeNegro,'porcentajeAmarillo':self.actualporcentajeAmarillo,'porcentajeCian':self.actualporcentajeCian})
                else:
                    raise exceptions.UserError("No existen cantidades en el almacen para el producto " + self.producto.name)
            else:
                    raise exceptions.UserError("No hay inventario en la ubicación selecionada")
    def test(self):
        i=self.env['tfs.tfs'].search([[]])
        raise RedirectWarning('mensaje',i[0],_('Test'))
    @api.multi
    def valida(self):
        view = self.env.ref('tfs.view_tfs_ticket')
        wiz = self.env['tfs.ticket'].create({'tfs_ids': [(4, self.id)]})
        self.write({'estado':'Confirmado'})
        #self.env['dcas.dcas'].create({'serie':self.serie.id,'contadorMono':self.actualMonocromatico,'contadorColor':self.actualColor,'fuente':'tfs.tfs'})
        In=self.inventario.search([['product_id.name','=',self.producto.name],['location_id','=',self.almacen.lot_stock_id.id]]).sorted(key='quantity',reverse=True)
        if(len(In)>0):
            In[0].write({'quantity':In[0].quantity-1})

        return {
                'name': _('Alerta'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'tfs.ticket',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }


    #@api.onchange('cliente')
    #def onchange_cliente(self):
    #    res = {}
    #    for record in self:
     #       res['domain'] = {'localidad': ['&',('parent_id.id', '=', record.cliente.id),('type', '=', 'delivery')]}
      #      record['usuario']=self.env.user.partner_id.id
      #  return res
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('tfs')
        result = super(tfs, self).create(vals)
        return result
    
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
    
    @api.onchange('actualMonocromatico')
    def _onchange_mono(self):
        if(self.productoNegro):
            rendimientoMono=self.actualMonocromatico-self.contadorAnteriorMono
            porcentaje=(100*rendimientoMono)/self.productoNegro.x_studio_rendimiento_toner if self.productoNegro.x_studio_rendimiento_toner>0 else 1
            self.actualporcentajeNegro=porcentaje
        

    @api.onchange('actualColor')
    def _onchange_color(self):
        if(self.productoCian):
            rendimientoMono=self.actualColor-self.contadorAnteriorCian
            porcentaje=(100*rendimientoMono)/self.productoCian.x_studio_rendimiento_toner if self.productoCian.x_studio_rendimiento_toner>0 else 1
            self.actualporcentajeCian=porcentaje
        if(self.productoAmarillo):
            rendimientoMono=self.actualColor-self.contadorAnteriorAmarillo
            porcentaje=(100*rendimientoMono)/self.productoAmarillo.x_studio_rendimiento_toner if self.productoAmarillo.x_studio_rendimiento_toner>0 else 1
            self.actualporcentajeAmarillo=porcentaje
        if(self.productoMagenta):
            rendimientoMono=self.actualColor-self.contadorAnteriorMagenta
            porcentaje=(100*rendimientoMono)/self.productoMagenta.x_studio_rendimiento_toner if self.productoMagenta.x_studio_rendimiento_toner>0 else 1
            self.actualporcentajeMagenta=porcentaje
    
    #@api.depends('tipo')
    #def type(self):
    #    for record in self:
    #        if(record.tipo):


    #@api.depends('almacen')
    #def cambio(self):
    #    res={}
    #    for record in self:
    #        if record.almacen:
    #            record['domi']=0
                #record.almacenlot_stock_id.id
                
                #res['domain'] = {'serie': [('x_studio_ubicacion_id', '=', record.almacen.lot_stock_id.id)]}
        #return res
    @api.multi
    @api.onchange('serie')
    def ultimoContador(self):
        i=0
        res={}
        for record in self:
            if record.serie:
                if(record.serie.x_studio_mini==False):
                    raise exceptions.UserError("El No. de Serie"+ record.serie.name+"no corresponde a Mini Almacen" )
                if(len(record.serie.x_studio_move_line)>0):
                    cliente = record.serie.x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id if(len(record.serie.x_studio_move_line)>1) else record.serie.x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id
                    localidad=record.serie.x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.id if(len(record.serie.x_studio_move_line)>1) else record.serie.x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.id
                    record['cliente'] = cliente
                    record['localidad'] = localidad
                    record['almacen'] =self.env['stock.warehouse'].search([['x_studio_field_E0H1Z','=',localidad]]).lot_stock_id.x_studio_almacn_padre.id
                if(record.colorBN=="B/N"):
                    data=record.serie.product_id.x_studio_toner_compatible.filtered(lambda x: 'Toner' in x.categ_id.name).mapped('id')
                    res['domain'] = {'productoNegro': [('id', 'in', data)]}
                    dc=self.env['dcas.dcas'].search([['serie','=',record.serie.id],['fuente','=','tfs.tfs'],['x_studio_toner_negro','=',1]]).sorted(key='create_date',reverse=True)
                    record['contadorMono'] =dc[0].id if(len(dc)>0) else self.env['dcas.dcas'].search([['serie','=',record.serie.id]]).sorted(key='create_date',reverse=True)[0].id

                if(record.colorBN=="Color"):
                    negro=record.serie.product_id.x_studio_toner_compatible.filtered(lambda x: 'Toner' in x.categ_id.name and x.x_studio_color=='Negro').mapped('id')
                    cian=record.serie.product_id.x_studio_toner_compatible.filtered(lambda x: 'Toner' in x.categ_id.name and x.x_studio_color=='Cian').mapped('id')
                    amarillo=record.serie.product_id.x_studio_toner_compatible.filtered(lambda x: 'Toner' in x.categ_id.name and x.x_studio_color=='Amarillo').mapped('id')
                    magenta=record.serie.product_id.x_studio_toner_compatible.filtered(lambda x: 'Toner' in x.categ_id.name and x.x_studio_color=='Magenta').mapped('id')                    
                    res['domain'] = {'productoNegro': [('id', 'in', negro)],'productoCian': [('id', 'in', cian)],'productoAmarillo': [('id', 'in', amarillo)],'productoMagenta': [('id', 'in', magenta)]}
                    dc=self.env['dcas.dcas'].search([['serie','=',record.serie.id],['fuente','=','tfs.tfs'],['x_studio_toner_negro','=',1]]).sorted(key='create_date',reverse=True)
                    dc1=self.env['dcas.dcas'].search([['serie','=',record.serie.id],['fuente','=','tfs.tfs'],['x_studio_toner_amarillo','=',1]]).sorted(key='create_date',reverse=True)
                    dc2=self.env['dcas.dcas'].search([['serie','=',record.serie.id],['fuente','=','tfs.tfs'],['x_studio_toner_cian','=',1]]).sorted(key='create_date',reverse=True)
                    dc3=self.env['dcas.dcas'].search([['serie','=',record.serie.id],['fuente','=','tfs.tfs'],['x_studio_toner_magenta','=',1]]).sorted(key='create_date',reverse=True)
                    record['contadorMono'] =dc[0].id if(len(dc)>0) else self.env['dcas.dcas'].search([['serie','=',record.serie.id]]).sorted(key='create_date',reverse=True)[0].id
                    record['contadorAmarillo'] =dc1[0].id if(len(dc1)>0) else self.env['dcas.dcas'].search([['serie','=',record.serie.id]]).sorted(key='create_date',reverse=True)[0].id
                    record['contadorCian'] =dc2[0].id if(len(dc2)>0) else self.env['dcas.dcas'].search([['serie','=',record.serie.id]]).sorted(key='create_date',reverse=True)[0].id
                    record['contadorMagenta'] =d3[0].id if(len(dc3)>0) else self.env['dcas.dcas'].search([['serie','=',record.serie.id]]).sorted(key='create_date',reverse=True)[0].id
                
  
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
