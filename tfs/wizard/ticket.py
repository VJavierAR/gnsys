from odoo import fields, models, _
from odoo.exceptions import UserError


class StockImmediateTransfer(models.TransientModel):
    _name = 'tfs.ticket'
    _description = 'Creacion de ticket'
    tfs_ids = fields.Many2many('tfs.tfs', 'tfs_tsf_ticket_rel')


    def forzar(self):
    	for r in self.tfs_ids:
    		r.write({'estado':'Valido'})

    def crear_ticker(self):
    	self.env['helpdesk.ticket'].create({'name':'Falla en rendimiento'})

