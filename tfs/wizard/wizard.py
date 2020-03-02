from odoo import fields, models, _
from odoo.exceptions import UserError


class StockImmediateTransfer(models.TransientModel):
    _name = 'tfs.ticket'
    _description = 'Creacion de ticket'
    tfs_ids = fields.Many2many('tfs.tfs', 'tfs_tsf_ticket_rel')


    def forzar(self):
    	for r in self.tfs_ids:
    		r.write({'estado':'Valido'})

    def crear_ticket(self):
    	for r in self.tfs_ids:
    		self.env['helpdesk.ticket'].create({'name':'Falla en rendimiento','x_studio_equipo_por_nmero_de_serie':[(4,r.serie.id)]})

