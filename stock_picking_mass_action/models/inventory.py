from odoo import _, fields, api
from odoo.models import Model
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import logging, ast
_logger = logging.getLogger(__name__)

class StockPicking(Model):
    _inherit = 'stock.inventory'    

    def _action_done(self):
    negative = next((line for line in self.mapped('line_ids') if line.product_qty < 0 and line.product_qty != line.theoretical_qty), False)
    if negative:
        raise UserError(_('You cannot set a negative product quantity in an inventory line:\n\t%s - qty: %s') % (negative.product_id.name, negative.product_qty))
    self.action_check()
    self.write({'state': 'done'})
    self.post_inventory()
    for r in self.mapped('line_ids'):
        log(str(r.id), level='info')
    return True