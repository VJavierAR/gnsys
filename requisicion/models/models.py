# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product_requisicion(models.Model):
    _name = 'product.rel.requisicion'
    _description='Rel requisiocion'
    cantidad=fields.Integer()
    product=fields.Many2one('product.product','id')
    req_rel=fields.Many2one('requisicion.requisicion','id')
    costo=fields.Float()
    ticket=fields.Many2one('helpdesk.ticket')
    direccion=fields.Char()
    cliente=fields.Many2one('res.partner')

    @api.onchange('cliente')
    def direc(self):
        self.direccion=str(self.cliente.street_name)+','+str(self.cliente.street_number)+','+str(self.cliente.street_number2)+','+str(self.cliente.l10n_mx_edi_colony)+','+str(self.cliente.state_id.name)+','+str(self.cliente.zip)





class requisicion(models.Model):
    _name = 'requisicion.requisicion'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description='Requisicion'
    name = fields.Char()
    area = fields.Selection([('Ventas','Ventas'),('Almacen','Almacen'), ('Mesa de Ayuda','Mesa de Ayuda')])
    fecha_prevista=fields.Datetime()
    justificacion=fields.Text()
    product_rel=fields.One2many('product.rel.requisicion','req_rel')
    state = fields.Selection([('draft','Nuevo'),('open','Proceso'), ('done','Hecho')],'State')
    origen=fields.Char()
    orden=fields.Char('Orden de Compra')
    @api.one
    def update_estado(self):
        self.write({'state':'open'})
    @api.one
    def update_estado1(self):
        self.write({'state':'done'})
        for record in self:
            ordenDCompra=self.env['purchase.order'].sudo().create({'partner_id':3,'date_planned':record.fecha_prevista})
            for line in record.product_rel:
                lineas=self.env['purchase.order.line'].sudo().create({'name':line.product.description,'product_id':line.product.id,'product_qty':line.cantidad,'price_unit':line.costo,'taxes_id':[10],'order_id':ordenDCompra.id,'date_planned':record.fecha_prevista,'product_uom':'1'})
            record['orden']=ordenDCompra.name

    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('requisicion')
        result = super(requisicion, self).create(vals)
        return result
