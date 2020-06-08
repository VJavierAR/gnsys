# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product_requisicion(models.Model):
    _name = 'product.rel.requisicion'
    _description='Rel requisiocion'
    cantidad=fields.Integer()
    product=fields.Many2one('product.product','Producto')
    req_rel=fields.Many2one('requisicion.requisicion')
    costo=fields.Float()
    ticket=fields.Many2one('helpdesk.ticket')
    direccion=fields.Char(compute='direc')
    cliente=fields.Many2one('res.partner')
    solicitar=fields.Boolean('Solicitar',default=True)
    pedido=fields.Char('Pedido')
    proveedor=fields.Char('proveedor')


    @api.depends('cliente')
    def direc(self):
        for recor in self:
            recor.direccion=str(recor.cliente.street_name)+','+str(recor.cliente.street_number)+','+str(recor.cliente.street_number2)+','+str(recor.cliente.l10n_mx_edi_colony)+','+str(recor.cliente.state_id.name)+','+str(recor.cliente.zip)





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
    picking_ids=fields.Many2many('stock.picking','picking_req_rel','picking_id','req_id')
    
    @api.one
    def update_estado(self):
        self.write({'state':'open'})



    @api.one
    def update_estado1(self):
        _logger.info(str(self.product_rel.mapped('product.x_studio_field_7aUDq.id')))
        pp=self.product_rel.filtered(lambda x:x.cantidad!=0)
        pro=self.product_rel.mapped('product.x_studio_field_7aUDq.id')
        cadena=""
        #data=record.product_rel.search([['pedido','=',False],['solicitar','=',True]])
        for prov in pro:
            ordenDCompra=self.env['purchase.order'].sudo().create({'partner_id':prov,'date_planned':record.fecha_prevista,'x_studio_field_a4rih':'Almacén'})
            cadena=cadena+ordenDCompra.name+','
            ppp=pp.filtered(lambda x: x.product.x_studio_field_7aUDq.id==prov)
            for prod in ppp:
                if(line.product.id not in d):
                    h=list(filter(lambda c:c['product']['id']==prod.product.id,ppp))
                    e=data.search([['product','=',prod.product.id]])
                    for hi in h:
                        t=t+hi.cantidad
                    e.write({'pedido':ordenDCompra.name})
                    lineas=self.env['purchase.order.line'].sudo().create({'name':prod.product.description if(prod.product.description) else '|','product_id':prod.product.id,'product_qty':t,'price_unit':prod.costo,'taxes_id':[10],'order_id':ordenDCompra.id,'date_planned':record.fecha_prevista,'product_uom':'1'})
                    d.append(line.product.id)
                    
        ppp=pp.filtered(lambda x: x.product.x_studio_field_7aUDq.id==False)
        if(len(ppp)>0):
            ordenDCompra=self.env['purchase.order'].sudo().create({'partner_id':3,'date_planned':record.fecha_prevista,'x_studio_field_a4rih':'Almacén'})
            cadena=cadena+ordenDCompra.name+','
            for prod in ppp:
                if(line.product.id not in d):
                    h=list(filter(lambda c:c['product']['id']==prod.product.id,ppp))
                    e=data.search([['product','=',prod.product.id]])
                    for hi in h:
                        t=t+hi.cantidad
                    e.write({'pedido':ordenDCompra.name})
                    lineas=self.env['purchase.order.line'].sudo().create({'name':prod.product.description if(prod.product.description) else '|','product_id':prod.product.id,'product_qty':t,'price_unit':prod.costo,'taxes_id':[10],'order_id':ordenDCompra.id,'date_planned':record.fecha_prevista,'product_uom':'1'})
                    d.append(line.product.id)

        record['orden']=cadena
        # if(self.orden==False):
        #     self.orden='|'
        # d=[]
        # for record in self:
        #     data=record.product_rel.search([['pedido','=',False],['solicitar','=',True]])
        #     if(len(data)>0):
        #         ordenDCompra=self.env['purchase.order'].sudo().create({'partner_id':3,'date_planned':record.fecha_prevista,'x_studio_field_a4rih':'Almacén'})
        #         for line in data:
        #             if(line.product.id not in d):
        #                 h=list(filter(lambda c:c['product']['id']==line.product.id,record.product_rel))
        #                 t=0
        #                 e=data.search([['product','=',line.product.id]])
        #                 for hi in h:
        #                     t=t+hi.cantidad
        #                 e.write({'pedido':ordenDCompra.name})
        #                 lineas=self.env['purchase.order.line'].sudo().create({'name':line.product.description if(line.product.description) else '|','product_id':line.product.id,'product_qty':t,'price_unit':line.costo,'taxes_id':[10],'order_id':ordenDCompra.id,'date_planned':record.fecha_prevista,'product_uom':'1'})
        #                 d.append(line.product.id)
        #         ot=len(record.product_rel.search([['pedido','=',False]]))
        #         if(ot==0):
        #             self.write({'state':'done'})
        #         record['orden']=self.orden+','+ordenDCompra.name

    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('requisicion')
        result = super(requisicion, self).create(vals)
        return result
