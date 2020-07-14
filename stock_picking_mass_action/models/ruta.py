from odoo import _, fields, api
from odoo.models import Model
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import logging, ast
_logger = logging.getLogger(__name__)
class CreacionRuta(Model):
    _name='creacion.ruta'
    _description='Ruta Gnsys'
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
    #almacen=fields.Many2one('stock.warehouse')
    #picking_type=fields.Many2many('stock.picking.type')
    usuarios=fields.Many2many('res.users')
    
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
            odometroAnterior=self.env['registro.odometro'].search([['rel_vehiculo','=',self.vehiculo.id]],order='id desc',limit=1)
            if(odometroAnterior.odometro>=self.odometro):
                raise UserError(_('Registro de odometro invalido debe ser mayor al anterior. Favor de revisar'))    
            if(self.odometro>odometroAnterior.odometro): 
                self.env['registro.odometro'].sudo().create({'rel_vehiculo':self.vehiculo.id,'odometro':self.odometro,'nivel_tanque':self.nivel_tanque,'chofer':self.chofer.id})
            self.ticket=t
        else:
            raise UserError(_('No se ha selaccionado ninguna orden'))
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('ruta') or _('New')
        result = super(CreacionRuta, self).create(vals)
        return result
    
    @api.onchange('tipo')
    def dominio(self):
        res={}
        operacion=self.env['stock.picking.type'].search([['code','=','outgoing']])
        u=operacion.search([['x_studio_field_B2WwI','=',self.env.uid],['code','=','outgoing']])
        res['domain']={'ordenes':["&","&","&",["picking_type_id.id","in",u.mapped('id')],["ruta_id","=",False],["state","=","assigned"],["state","!=","done"]]}
        self.usuarios=[(6,0,u.mapped('x_studio_field_B2WwI.id'))]
        _logger.info(u.mapped('x_studio_field_B2WwI.id'))
        return res
        