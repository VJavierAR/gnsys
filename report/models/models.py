# -*- coding: utf-8 -*-

from odoo import models, fields, api
class report(models.Model):
	_inherit = 'stock.picking'
	value2 = fields.Integer(compute="_value_pc", store=True)

	@api.depends('state')
	def _value_pc(self):
		for record in self:
			if('SU' in record.name):
				record['value2'] = 1
			if('RE' in record.name):
				record['value2']=2
