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
    _inherit = ['mail.thread', 'mail.activity.mixin']    
    _name = 'tfs.tfs'
    _description='tfs'
    name = fields.Char()
    almacen = fields.Many2one('stock.warehouse', "Almacen",store='True',compute='onchange_localidad')
    tipo = fields.Selection([('Cian', 'Cian'),('Magenta','Magenta'),('Amarillo','Amarillo'),('Negro','Negro')])
    usuario = fields.Many2one('res.partner')
    inventario = fields.One2many(comodel='stock.quant',related='almacen.lot_stock_id.quant_ids', string="Quants")
    cliente = fields.Many2one('res.partner', store=True,string='Cliente')
    localidad=fields.Many2one('res.partner',store='True',string='Localidad')
    serie=fields.Many2one('stock.production.lot',string='Numero de Serie',store='True')
    domi=fields.Integer()
    producto=fields.Many2one('product.product',string='Toner')
    contadorAnterior=fields.Many2one('dcas.dcas',string='Anterior',compute='type',store=True)
    contadorAnteriorMono=fields.Integer(related='contadorAnterior.contadorMono',string='Monocromatico',store=True)
    contadorAnteriorColor=fields.Integer(related='contadorAnterior.contadorColor',string='Color',store=True)
    porcentajeAnteriorNegro=fields.Integer(related='contadorAnterior.porcentajeNegro',string='Negro',store=True)
    porcentajeAnteriorCian=fields.Integer(related='contadorAnterior.porcentajeCian',string='Cian',store=True)
    porcentajeAnteriorAmarillo=fields.Integer(related='contadorAnterior.porcentajeAmarillo',string='Amarillo',store=True)
    porcentajeAnteriorMagenta=fields.Integer(related='contadorAnterior.porcentajeMagenta',string='Magenta',store=True)
    actualMonocromatico=fields.Integer(string='Contador Monocromatico')
    actualColor=fields.Integer(string='Contador Color')
    actualporcentajeNegro=fields.Integer(string='Toner Negro %')
    actualporcentajeAmarillo=fields.Integer(string='Toner Amarillo %')
    actualporcentajeCian=fields.Integer(string='Toner Cian %')
    actualporcentajeMagenta=fields.Integer(string='Toner Magenta%')
    evidencias=fields.One2many('tfs.evidencia',string='Evidencias',inverse_name='tfs_id')
    estado=fields.Selection([('borrador','Borrador'),('xValidar','Por Validar'),('Valido','Valido'),('Confirmado','Confirmado')])
    
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
                            self.env['dcas.dcas'].create({'x_studio_toner_'+str(self.tipo).lower():1,'serie':record.serie.id,'contadorMono':record.actualMonocromatico,'contadorColor':record.actualColor,'fuente':'tfs.tfs'})
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
                            self.env['dcas.dcas'].create({'x_studio_toner_'+str(self.tipo).lower():1,'serie':record.serie.id,'contadorMono':record.actualMonocromatico,'contadorColor':record.actualColor,'fuente':'tfs.tfs'})
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
    
    @api.depends('producto')
    def onchange_localidad(self):
        res={}
        for record in self:
            if record.localidad:
                record['almacen'] =self.env['stock.warehouse'].search([['x_studio_field_E0H1Z','=',record.localidad.id]]).lot_stock_id.x_studio_almacn_padre
                self.tipo=record.producto.x_studio_color
    
    @api.depends('tipo')
    def type(self):
        for record in self:
            if(record.tipo):
                dc=self.env['dcas.dcas'].search([['serie','=',record.serie.id],['fuente','=','tfs.tfs'],['x_studio_toner_'+str(record.tipo).lower(),'=',1]]).sorted(key='create_date',reverse=True)
                _logger.info('hhhhhhhhhhhhhhhhhh'+str(dc))
                _logger.info('x_studio_toner_'+str(record.tipo).lower())
                if(len(dc)>0):
                    record['contadorAnterior']=dc[0].id 

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
    @api.onchange('serie')
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
