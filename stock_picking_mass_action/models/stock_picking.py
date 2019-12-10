from odoo import _, fields, api
from odoo.models import Model

class StockPicking(Model):
    _inherit = 'stock.picking'
    almacenOrigen=fields.Many2one('stock.warehouse','Almacen Origen')
    almacenDestino=fields.Many2one('stock.warehouse','Almacen Destino')
    hiden=fields.Integer(compute='hide')
    ajusta=fields.Boolean('Ajusta')
    
    #@api.onchange('ajusta')
    #def ajus(self):
    #    for record in self:
     #       if(record.sale_id):
      #          pedido=record.sale_id
       #     record['state']='draft'
        #    if(record.ajusta):
         #       for s in record.move_ids_without_package:
          #          if (s.product_id.id!=s.x_studio_field_mpmwm):
           #             self.env.cr.execute("delete from stock_move_line where move_id = "+str(s.x_studio_id)+";")
            #            self.env.cr.execute("delete from stock_move where origin = '" + record.origin + "' and product_id="+str(s.x_studio_field_mpmwm)+";")
             #           self.env.cr.execute("delete from sale_order_line where  order_id = " + str(pedido.id) + " and product_id="+str(s.x_studio_field_mpmwm)+";")
              #          self.env.cr.execute("delete from stock_move where id =" + str(s.x_studio_id)+";")
    
    def action_toggle_is_locked(self):
        self.ensure_one()
        for record in self:
            if(record.sale_id):
                pedido=record.sale_id
            #    record['state']='draft'
            if(self.is_locked==False):
                for s in record.move_ids_without_package:
                    if (s.product_id.id!=s.x_studio_field_mpmwm):
                        self.env.cr.execute("delete from stock_move_line where move_id = "+str(s.x_studio_id)+";")
                        self.env.cr.execute("delete from stock_move where origin = '" + record.origin + "' and product_id="+str(s.x_studio_field_mpmwm)+";")
                        self.env.cr.execute("delete from sale_order_line where  order_id = " + str(pedido.id) + " and product_id="+str(s.x_studio_field_mpmwm)+";")
                        self.env.cr.execute("delete from stock_move where id =" + str(s.x_studio_id)+";")
        self.is_locked = not self.is_locked
        return True
    
    @api.depends('picking_type_id')
    def hide(self):
        for record in self:
            if(record.picking_type_id):
                if('internas' in record.picking_type_id.name or 'Internal' in record.picking_type_id.name):
                    record['hiden']=1
    
    @api.onchange('almacenOrigen')
    def cambioOrigen(self):
        self.location_id=self.almacenOrigen.lot_stock_id.id
    
    @api.onchange('almacenDestino')
    def cambioDestino(self):
        self.location_dest_id=self.almacenDestino.lot_stock_id.id
    
    
    @api.model
    def check_assign_all(self):
        """ Try to assign confirmed pickings """
        domain = [('picking_type_code', '=', 'outgoing'),
                  ('state', '=', 'confirmed')]
        records = self.search(domain, order='scheduled_date')
        records.action_assign()

    def action_immediate_transfer_wizard(self):
        view = self.env.ref('stock.view_immediate_transfer')
        wiz = self.env['stock.immediate.transfer'].create(
            {'pick_ids': [(4, p.id) for p in self]})
        return {
            'name': _('Immediate Transfer?'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.immediate.transfer',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }
class StockPicking(Model):
    _inherit = 'stock.move'
    almacenOrigen=fields.Many2one('stock.warehouse','Almacen Origen')
    
    @api.onchange('product_id')
    def chanProduct(self):
        for record in self:
            if('SU' in record.picking_id.name and record.origin!=False and record.product_id!=False and 'SO' in record.origin):
                sale=self.sudo().env['sale.order'].search([['name','=',record.origin]])
                moveAnterior=self.sudo().env['stock.move'].browse(record.x_studio_id)
                #record['x_studio_anterior_product']=moveAnterior.product_id.id
                #produc=record.product_id.id
                dic={}
                dic['product_uom']=record.product_uom.id
                dic['product_uom_qty']=record.product_uom_qty
                dic['product_id']=record.product_id.id
                dic['name']=record.name
                dic['price_unit']=0.00
                dic['order_id']=sale.id
                self.sudo().env['sale.order.line'].create(dic)
            
    @api.onchange('almacenOrigen')
    def cambioOrigen(self):
        self.location_id=self.almacenOrigen.lot_stock_id.id
