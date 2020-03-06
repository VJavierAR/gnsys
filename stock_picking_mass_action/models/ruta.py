from odoo import _, fields, api
from odoo.models import Model
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import logging, ast
_logger = logging.getLogger(__name__)

class CreacionRuta(Model):
	_name='creacion.ruta'
	name=fields.Char()
	chofer=fields.Many2one('hr.employee')
	vehiculo=fields.Many2one('automovil')
	ordenes=fields.Many2many('stock.picking')
	zona=fields.Selection([["SUR","SUR"],["NORTE","NORTE"],["PONIENTE","PONIENTE"],["ORIENTE","ORIENTE"],["CENTRO","CENTRO"],["DISTRIBUIDOR","DISTRIBUIDOR"],["MONTERREY","MONTERREY"],["CUERNAVACA","CUERNAVACA"],["GUADALAJARA","GUADALAJARA"],["QUERETARO","QUERETARO"],["CANCUN","CANCUN"],["VERACRUZ","VERACRUZ"],["PUEBLA","PUEBLA"],["TOLUCA","TOLUCA"],["LEON","LEON"],["COMODIN","COMODIN"],["VILLAHERMOSA","VILLAHERMOSA"],["MERIDA","MERIDA"],["VERACRUZ","VERACRUZ"],["ALTAMIRA","ALTAMIRA"]])
	estado=fields.Selection([["borrador","Borrador"],["valido","Confirmado"]])
	odoometro=fields.Integer()
	nivel_tanque=fields.Selection([["reserva","Reserva"],[".25","1/4"],[".5","1/2"],[".75","3/4"],["1","Lleno"]])
	@api.multi
	def confirmar(self):
		#self.estado="valido"
		self.ordenes.write({'ruta_id':self.id})
		self.ordenes.write({'estado':'ruta'})
		self.ordenes.write({'ajusta':True})
		for o in self.ordenes:
			if(o.sale_id.x_studio_field_bxHgp):
				o.sale_id.x_studio_field_bxHgp.write({'stage_id':108})
		self.env['registro.odometro'].create({'rel_vehiculo':self.vehiculo.id,'odometro':self.odometro,'nivel_tanque':self.nivel_tanque}) 
	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('ruta') or _('New')
		result = super(CreacionRuta, self).create(vals)
		return result

