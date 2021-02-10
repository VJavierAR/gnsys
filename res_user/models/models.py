from odoo import models
import base64

class ResUser(models.Model):
    _inherit = "res.user"
    second_users=fields.One2many('second.user','rel_user')

class SecondUser(models.Model):
	rel_user=fields.Many2one('res.user')
	name=fields.Char()
	user=fields.Char()
	password=fields.Char(string='password')

	@api.model
    def create(self, vals):
    	password=vals['password']
    	password_bytes = password.encode('ascii')
    	base64_bytes = base64.b64encode(password_bytes)
    	base64_message = base64_bytes.decode('ascii')
        vals['password'] = base64_message
        result = super(SecondUser, self).create(vals)
        return result




		