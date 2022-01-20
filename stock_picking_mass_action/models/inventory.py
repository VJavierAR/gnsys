from odoo import _, fields, api
from odoo.models import Model
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import logging, ast
_logger = logging.getLogger(__name__)
import threading
from odoo.tools import OrderedSet
from collections import Counter, defaultdict

class StockPicking(Model):
    _inherit = 'stock.inventory'    

    def _action_done(self):
        negative = next((line for line in self.mapped('line_ids') if line.product_qty < 0 and line.product_qty != line.theoretical_qty), False)
        if negative:
            raise UserError(_('You cannot set a negative product quantity in an inventory line:\n\t%s - qty: %s') % (negative.product_id.name, negative.product_qty))
        threaded_calculation = threading.Thread(target=self.action_check(), args=())
        self.write({'state': 'done'})
        threaded_post = threading.Thread(target=self.post_inventory(), args=())
        for r in self.mapped('line_ids'):
            if(r.x_studio_field_yVDjd):
                i=self.env['stock.quant'].search([['product_id','=',r.product_id.id],['location_id','=',r.location_id.id]])
                i.sudo().write({'x_studio_field_kUc4x':r.x_studio_field_yVDjd.id})
        return True


class StockPic(Model):
    _inherit = 'stock.move'

    def _action_confirm(self, merge=True, merge_into=False):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        :param: merge: According to this boolean, a newly confirmed move will be merged
        in another move of the same picking sharing its characteristics.
        """
        move_create_proc = self.env['stock.move']
        move_to_confirm = self.env['stock.move']
        move_waiting = self.env['stock.move']

        to_assign = {}
        for move in self:
            # if the move is preceeded, then it's waiting (if preceeding move is done, then action_assign has been called already and its state is already available)
            if move.move_orig_ids:
                move_waiting |= move
            else:
                if move.procure_method == 'make_to_order':
                    move_create_proc |= move
                else:
                    move_to_confirm |= move
            if move._should_be_assigned():
                key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)
                if key not in to_assign:
                    to_assign[key] = self.env['stock.move']
                to_assign[key] |= move

        # create procurements for make to order moves
        for move in move_create_proc:
            values = move._prepare_procurement_values()
            origin = (move.group_id and move.group_id.name or (move.origin or move.picking_id.name or "/"))
            self.env['procurement.group'].run(move.product_id, move.product_uom_qty, move.product_uom, move.location_id, move.rule_id and move.rule_id.name or "/", origin,
                                              values)

        move_to_confirm.write({'state': 'confirmed'})
        (move_waiting | move_create_proc).write({'state': 'waiting'})

        # assign picking in batch for all confirmed move that share the same details
        for moves in to_assign.values():
            moves._assign_picking()
        self._push_apply()
        #if merge:
         #   return self._merge_moves(merge_into=merge_into)
        return self



class StockMoveLine(Model):
    _inherit = 'stock.move.line'
    def _create_and_assign_production_lot(self):
        """ Creates and assign new production lots for move lines."""
        lot_vals = []
        # It is possible to have multiple time the same lot to create & assign,
        # so we handle the case with 2 dictionaries.
        key_to_index = {}  # key to index of the lot
        key_to_mls = defaultdict(lambda: self.env['stock.move.line'])  # key to all mls
        for ml in self:
            key = (ml.company_id.id, ml.product_id.id, ml.lot_name)
            key_to_mls[key] |= ml
            if ml.tracking != 'lot' or key not in key_to_index:
                key_to_index[key] = len(lot_vals)
                lot_vals.append({
                    'company_id': ml.company_id.id,
                    'name': ml.lot_name,
                    'product_id': ml.product_id.id
                })

        lots = self.env['stock.production.lot'].create(lot_vals)
        for key, mls in key_to_mls.items():
            mls._assign_production_lot(lots[key_to_index[key]].with_prefetch(lots._ids))  # With prefetch to reconstruct the ones broke by accessing by index


    def _action_done(self):
        super(StockMoveLine, self)._action_done()
        ml_ids_to_delete = OrderedSet()
        ml_ids_to_create_lot = OrderedSet()
        ml_to_create_lot = self.env['stock.move.line'].browse(ml_ids_to_create_lot)
        ml_to_create_lot._create_and_assign_production_lot()
        mls_to_delete = self.env['stock.move.line'].browse(ml_ids_to_delete)
        mls_to_delete.unlink()
        mls_todo = (self - mls_to_delete)
        #mls_todo._check_company()
        ml_ids_to_ignore = OrderedSet()
        for ml in mls_todo:
            if ml.picking_id.picking_type_code=='outgoing':
                cliente = self.env['stock.warehouse'].search([['x_studio_field_E0H1Z','=',ml.picking_id.partner_id.id]])
                temp = ml.location_dest_id
                ml.location_dest_id = cliente.lot_stock_id.id if cliente.id else temp.id
                if ml.lot_id.id and cliente.id:
                    ml.lot_id.write({'x_studio_demo': True if(ml.picking_id.sale_id.x_studio_tipo_de_solicitud == 'Demostración') else False, 'x_studio_estado': 'Nuevo', 'servicio': ml.picking_id.sale_id.x_studio_field_69Boh.id, 'x_studio_cliente': ml.picking_id.partner_id.parent_id.id, 'x_studio_localidad_2': ml.picking_id.partner_id.id})

