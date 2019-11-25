from odoo import _, fields, api
from odoo.models import Model


class StockPicking(Model):
    _inherit = 'stock.picking'
    almacenOrigen=fields.Many2one('stock.warehouse','Almacen Origen')
    almacenDestino=fields.Many2one('stock.warehouse','Almacen Destino')
    hiden=fields.Integer(compute='hide')
    ajusta=fields.Boolean('Ajusta')
    
    @api.onchange('ajusta')
    def ajus(self):
        for record in self:
            pedido=record.sale_id
            record['state']='draft'
            if(record.ajusta):
                for s in record.move_ids_without_package:
                    if (s.product_id.id!=s.x_studio_field_mpmwm):
                        self.env.cr.execute("delete from stock_move_line where move_id = "+str(s.x_studio_id)+";")
                        self.env.cr.execute("delete from stock_move where origin = '" + record.origin + "' and product_id="+str(s.x_studio_field_mpmwm)+";")
                        self.env.cr.execute("delete from sale_order_line where  order_id = " + str(pedido.id) + " and product_id="+str(s.x_studio_field_mpmwm)+";")
                        self.env.cr.execute("delete from stock_move where id =" + str(s.x_studio_id)+";")
    
    
    
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
