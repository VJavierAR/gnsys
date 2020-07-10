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
	odometro=fields.Integer()
	nivel_tanque=fields.Selection([["reserva","Reserva"],[".25","1/4"],[".5","1/2"],[".75","3/4"],["1","Lleno"]])
	tipo=fields.Selection([["local","Local"],["foraneo","Foraneo"],["guadalajara","Guadalajara"],["monterrey","Monterrey"],["queretaro","Querétaro"]])
	EstadoPais=fields.Many2one('res.country.state',string="Estado")
	EstadoPaisName=fields.Char(related='EstadoPais.name',string="Estado")
	ticket=fields.Char()
	almacen=fields.Many2one('stock.warehouse')
	picking_type=fields.Many2one('stock.picking.type')
	
	# @api.onchange('tipo')
	# def domin(self):
	# 	res={}
	# 	if(self.tipo):
	# 		if(self.tipo=="local"):
	# 			res['domain']={'ordenes':["&","&","&","&",("ruta_id","=",False),("picking_type_id.id","=",2),('tipo','in',("Ciudad de México","Estado de México","México")),('state','!=','done'),('state','=','assigned')]}
	# 		if(self.tipo=="foraneo"):
	# 			res['domain']={'ordenes':["&","&","&","&",("ruta_id","=",False),("picking_type_id.id","=",2),('tipo','not in',("Ciudad de México","Estado de México","México","Querétaro","Jalisco","Nuevo León")),('state','!=','done'),('state','=','assigned')]}
	# 		if(self.tipo=="guadalajara"):
	# 			res['domain']={'ordenes':["&","&","&","&",("ruta_id","=",False),("picking_type_id.id","=",2),('tipo','=',"Guadalajara"),('state','!=','done'),('state','=','assigned')]}
	# 		if(self.tipo=="monterrey"):
	# 			res['domain']={'ordenes':["&","&","&","&",("ruta_id","=",False),("picking_type_id.id","=",2),('tipo','=',"Nuevo León"),('state','!=','done'),('state','=','assigned')]}
	# 		if(self.tipo=="queretaro"):
	# 			res['domain']={'ordenes':["&","&","&","&",("ruta_id","=",False),("picking_type_id.id","=",2),('tipo','=',"Querétaro"),('state','!=','done'),('state','=','assigned')]}
	# 	return res

	@api.multi
	def confirmar(self):
		t=""
		if(len(self.ordenes)>0):
			self.ordenes.write({'ruta_id':self.id})
			self.ordenes.write({'estado':'ruta'})
			self.ordenes.write({'ajusta':True})
			self.estado="valido"
			if(self.odometro==0 and self.tipo.lower()=="local"):
				raise UserError(_('Tiene que ingresas el Odometro'))
			for o in self.ordenes:
				if(o.sale_id.id):
					o.sale_id.x_studio_field_bxHgp.write({'stage_id':108})
					t=t+str(o.sale_id.x_studio_field_bxHgp.id)+','
				if(o.sale_id.id==False):
					t=t+str(o.origin)+','
			self.env['registro.odometro'].sudo().create({'rel_vehiculo':self.vehiculo.id,'odometro':self.odometro,'nivel_tanque':self.nivel_tanque,'chofer':self.chofer.id}) 
			self.ticket=t
		else:
			raise UserError(_('No se ha selaccionado ninguna orden'))


	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('ruta') or _('New')
		result = super(CreacionRuta, self).create(vals)
		return result

