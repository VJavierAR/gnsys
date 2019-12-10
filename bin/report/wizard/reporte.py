# Copyright 2014 Camptocamp SA - Guewen Baconnier
# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, api
from odoo.models import TransientModel


class StockPickingMassAction(TransientModel):
    _name = 'stock.picking.mass.action'
    _description = 'Stock Picking Mass Action'

    @api.model
    def _default_picking_ids(self):
        ordenes=self.env['stock.picking'].browse(self.env.context.get('active_ids'))
        #otro=self.env['otro.modelo'].create({'name':''})
        #for ord in ordenes:
         #   if(odr.state=='done'):
          #      self.env['otr2.model'].create({'otro_id':otro.id,'picking_id':ord.id})
        #return 
    
