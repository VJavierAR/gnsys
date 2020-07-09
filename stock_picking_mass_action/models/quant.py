from odoo import _, fields, api
from odoo.models import Model
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import logging, ast
_logger = logging.getLogger(__name__)
import threading

class StockQuan(Model):
    _inherit = 'stock.quant'
    quants_registro=fields.One2many('stock.quant.line','quant_id')


    @api.model
    def _unlink_zero_quants(self):
        """ _update_available_quantity may leave quants with no
        quantity and no reserved_quantity. It used to directly unlink
        these zero quants but this proved to hurt the performance as
        this method is often called in batch and each unlink invalidate
        the cache. We defer the calls to unlink in this method.
        """
        precision_digits = max(6, self.env.ref('product.decimal_product_uom').digits * 2)
        # Use a select instead of ORM search for UoM robustness.
        #query = """SELECT id FROM stock_quant WHERE round(quantity::numeric, %s) = 0 AND round(reserved_quantity::numeric, %s) = 0;"""
        #params = (precision_digits, precision_digits)
        #self.env.cr.execute(query, params)
        #quant_ids = self.env['stock.quant'].browse([quant['id'] for quant in self.env.cr.dictfetchall()])
        #quant_ids.sudo().unlink()

    @api.onchange('quantity')
    def actualizaRegla(self):
        if(self.x_studio_almacn.x_studio_mini==True):
            q=self.env['stock.warehouse.orderpoint'].search([['location_id','=',self.location_id.id],['product_id','=',self.product_id.id],['active','=',False]])
            q.x_studio_existencia=self.quantity

class StockQuantLine(Model):
    _name='stock.quant.line'
    _description='registro de cambios'
    descripcion=fields.Char()
    cantidadAnterior=fields.Float()
    cantidadReal=fields.Float()
    quant_id=fields.Many2one('stock.quant')
    usuario=fields.Many2one('res.users')