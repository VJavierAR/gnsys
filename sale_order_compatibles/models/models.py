# -*- coding: utf-8 -*-

from odoo import _, models, fields, api, tools
from email.utils import formataddr
from odoo.exceptions import UserError,RedirectWarning
from odoo import exceptions, _
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)


class sale_order_compatibles(models.Model):
	_name = 'sale_order_compatibles'
	saleOrder = fields.Many2one('sale.order')
	equipos = fields.Many2one('product.product', string = 'Equipos')
	cantidad = fields.Selection(selection = [(0, '0'),(1, '1')],string = 'Cantidad',default=1)
	estado = fields.Selection(selection = [('Nuevo', 'Nuevo'),('Usado', 'Usado')], default = 'Nuevo')
	componentes = fields.One2many('sale_order_compatibles_mini', 'saleOrderMini', string = 'Componentes')
	toner = fields.One2many('sale_order_compatibles_mini_toner', 'saleOrderMini', string = 'Toner')
	accesorios = fields.One2many('sale_order_compatibles_mini_acesorios', 'saleOrderMini', string = 'Accesorios')
	serie=fields.Many2one('stock.production.lot','Serie')
	domin=fields.Char()
	location=fields.Integer()
	tipo=fields.Char()
	precio=fields.Float(default=0.00)
	@api.onchange('equipos')
	def domi(self):
		datos=self.equipos.x_studio_toner_compatible.mapped('id')
		self.domin=str(datos)


class miniModelo(models.Model):
	_name = 'sale_order_compatibles_mini'
	idProducto = fields.Char(string = 'id Producto')
	producto = fields.Many2one('product.product')
	cantidad = fields.Integer(string = 'Cantidad')
	saleOrderMini=fields.Many2one('sale_order_compatibles')


	@api.onchange('idProducto')
	def domi(self):
		res={}
		if(self.idProducto and self.idProducto!='[]'):
			da=self.env['product.product'].browse(eval(self.idProducto)).filtered(lambda x:x.categ_id.id==7).mapped('id')
			res['domain']={'producto':[['id','in',da]]}
		return res


class miniModeloToner(models.Model):
	_name = 'sale_order_compatibles_mini_toner'
	idProducto = fields.Char(string = 'id Producto')
	producto = fields.Many2one('product.product')
	cantidad = fields.Integer(string = 'Cantidad')
	saleOrderMini=fields.Many2one('sale_order_compatibles')
	precio=fields.Float(default=0.00)
	tipo=fields.Char()

	@api.onchange('idProducto')
	def domi(self):
		res={}
		if(self.idProducto and self.idProducto!='[]'):
			da=self.env['product.product'].browse(eval(self.idProducto)).filtered(lambda x:x.categ_id.id==5).mapped('id')
			res['domain']={'producto':[['id','in',da]]}
		return res


class miniModeloAccesorio(models.Model):
	_name = 'sale_order_compatibles_mini_acesorios'
	idProducto = fields.Char(string = 'id Producto')
	producto = fields.Many2one('product.product')
	cantidad = fields.Integer(string = 'Cantidad')
	saleOrderMini=fields.Many2one('sale_order_compatibles')
	precio=fields.Float(default=0.00)
	tipo=fields.Char()

	@api.onchange('idProducto')
	def domi(self):
		res={}
		if(self.idProducto and self.idProducto!='[]'):
			da=self.env['product.product'].browse(eval(self.idProducto)).filtered(lambda x:x.categ_id.id!=5 and x.categ_id.id!=7).mapped('id')
			res['domain']={'producto':[['id','in',da]]}
		return res

class sale_update(models.Model):
	_inherit = 'sale.order'
	compatiblesLineas = fields.One2many('sale_order_compatibles', 'saleOrder', string = 'nombre temp',copy=True)

	serieRetiro2=fields.Many2one('stock.production.lot','Serie retiro')

	@api.onchange('serieRetiro2')
	def serieRetiro(self):
		for record in self:
		  if(record.serieRetiro2.id):
		    if(record.serieRetiro2.x_studio_localidad_2.id):
		      record['partner_id']=record.serieRetiro2.x_studio_localidad_2.parent_id.id
		      record['partner_shipping_id']=record.serieRetiro2.x_studio_localidad_2.id
		      record['compatiblesLineas']=[{'serie':record.serieRetiro2.id,'cantidad':1,'tipo':record.x_studio_tipo_de_solicitud,'equipos':record.serieRetiro2.product_id.id}]

	@api.multi
	def mail_action_quotation_send(self):
		'''
		This function opens a window to compose an email, with the edi sale template message loaded by default
		'''
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = ir_model_data.get_object_reference('sale', 'email_template_edi_sale')[1]
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'sale_email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False
		lang = self.env.context.get('lang')
		template = template_id and self.env['mail.template'].browse(template_id)
		if template and template.lang:
			lang = template._render_template(template.lang, 'sale.order', self.ids[0])
		ctx = {
			'default_model': 'sale.order',
			'default_res_id': self.ids[0],
			#'default_use_template': bool(template_id),
			#'default_template_id': template_id,
			'default_composition_mode': 'comment',
			'mark_so_as_sent': True,
			'model_description': self.with_context(lang=lang).type_name,
			'custom_layout': "mail.mail_notification_paynow",
			'proforma': self.env.context.get('proforma', False),
			'force_email': True
		}
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}

	def preparaSolicitud(self):
		self.order_line.unlink()
		data=[]
		if(len(self.compatiblesLineas)>0):
			for e in self.compatiblesLineas:
				if(e.cantidad!=0):
					d={'x_studio_estado':e.estado,'x_studio_field_mqSKO':e.equipos.id,'product_id':e.equipos.id,'name':e.equipos.name,'product_uom_qty':1,'product_uom':e.equipos.uom_id.id,'price_unit':e.precio,'x_studio_id_relacion':e.id}
					self.order_line=[d]
				for e1 in e.componentes:
					if(e1.cantidad!=0):
						d={'x_studio_field_mqSKO':e1.producto.id,'product_id':e1.producto.id,'name':e1.producto.name,'product_uom_qty':e1.cantidad,'product_uom':e1.producto.uom_id.id,'price_unit':e1.precio,'x_studio_id_relacion':e.id,'x_studio_modelo':e.equipos.name}
						self.order_line=[d]
				for e2 in e.toner:
					if(e2.cantidad!=0):
						d={'x_studio_field_mqSKO':e2.producto.id,'product_id':e2.producto.id,'name':e2.producto.name,'product_uom_qty':e2.cantidad,'product_uom':e2.producto.uom_id.id,'price_unit':e2.precio,'x_studio_id_relacion':e.id,'x_studio_modelo':e.equipos.name}
						self.order_line=[d]
				for e3 in e.accesorios:
					if(e3.cantidad!=0):
						d={'x_studio_field_mqSKO':e3.producto.id,'product_id':e3.producto.id,'name':e3.producto.name,'product_uom_qty':e3.cantidad,'product_uom':e3.producto.uom_id.id,'price_unit':e3.precio,'x_studio_id_relacion':e.id,'x_studio_modelo':e.equipos.name}
						self.order_line=[d]
			self.write({'state':'sent'})
		if(self.x_studio_tipo_de_solicitud=="Venta" or self.x_studio_tipo_de_solicitud=="Venta directa"):
			template_id=self.env['mail.template'].search([('id','=',58)], limit=1)
			template_id.send_mail(self.id, force_send=True)
		if(self.x_studio_tipo_de_solicitud!="Venta" or self.x_studio_tipo_de_solicitud!="Venta directa"):
			if(len(self.compatiblesLineas)==0):
				raise UserError(_('No hay registros a procesar'))
			else:
				template_id=self.env['mail.template'].search([('id','=',58)], limit=1)
				template_id.send_mail(self.id, force_send=True)
	
	def desbloquea(self):
		self.action_cancel()
		self.action_draft()
		picks=self.env['stock.picking'].search([['sale_id','=',self.id]])
		picks.unlink()

	def componentes(self):
		if(len(self.order_line)>0):
			for s in self.order_line:
				for ss in s.x_studio_field_9nQhR.x_studio_histrico_de_componentes:
					d={'x_studio_field_mqSKO':ss.x_studio_field_gKQ9k.id,'product_id':ss.x_studio_field_gKQ9k.id,'name':ss.x_studio_field_gKQ9k.name,'product_uom_qty':ss.x_studio_cantidad,'product_uom':ss.x_studio_field_gKQ9k.uom_id.id,'price_unit':0.00}
					self.order_line=[d]
	@api.multi
	def action_confirm(self):
	    if self._get_forbidden_state_confirm() & set(self.mapped('state')):
	        raise UserError(_(
	            'It is not allowed to confirm an order in the following states: %s'
	        ) % (', '.join(self._get_forbidden_state_confirm())))

	    for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
	        order.message_subscribe([order.partner_id.id])
	    self.write({
	        'state': 'sale',
	        'confirmation_date': fields.Datetime.now()
	    })
	    self._action_confirm()
	    if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
	        self.action_done()
	    self.saleLinesMove()
	    return True

	def saleLinesMove(self):
		picks=self.env['stock.picking'].search(['&',['sale_id','=',self.id],['state','!=','draft']])
		sal=self.order_line.sorted(key='id').mapped('id')
		cliente=self.partner_shipping_id
		for p in picks:
			i=0
			for pi in p.move_ids_without_package.sorted(key='id'):
				pi.write({'sale_line_id':sal[i]})
				if(p.picking_type_id.code=='outgoing' and 'REFACCIONES' not in p.sale_id.warehouse_id.name):
					almacen=self.env['stock.warehouse'].search([['x_studio_field_E0H1Z','=',cliente.id]])
					if(almacen.id!=False):
						pi.write({'location_dest_id':almacen.lot_stock_id.id})
						self.env['stock.move.line'].search([['move_id','=',pi.id]]).write({'location_dest_id':almacen.lot_stock_id.id})
				i=i+1

	def cambio(self):
		self.action_confirm()
		picks=self.env['stock.picking'].search([['sale_id','=',self.id]])
		almacen=self.env['stock.warehouse'].search([['x_studio_field_E0H1Z','=',self.partner_shipping_id.id]])
		for pic in picks:
			ppp=pic.copy()
			ppp.write({'retiro':True})
			#ppp.order_line=[(5,0,0)]
			if('PICK' in ppp.name or 'SU' in ppp.name):
				ppp.write({'location_id':almacen.lot_stock_id.id})
				ppp.write({'location_dest_id':pic.picking_type_id.default_location_dest_id.id})
				i=0
				for e in self.compatiblesLineas:
					ppp.move_ids_without_package[i].write({'location_id':almacen.lot_stock_id.id,'location_dest_id':pic.picking_type_id.default_location_dest_id.id,'product_id':e.serie.product_id.id,'x_studio_serie_destino':e.serie.id})
					#self.env['stock.move.line'].search([['picking_id','=',ppp.id]]).write({'location_id':almacen.lot_stock_id.id})
					#ppp.move_ids_without_package[i].write({'location_dest_id':ppp.picking_type_id.default_location_dest_id.id})
					i=i+1
			if('PACK' in ppp.name or 'TRA' in ppp.name):
				ppp.write({'location_id':ppp.picking_type_id.default_location_src_id.id})
				ppp.write({'location_dest_id':ppp.picking_type_id.default_location_dest_id.id})
				#ppp.move_ids_without_package.write({'location_id':ppp.picking_type_id.default_location_src_id.id})
				#self.env['stock.move.line'].search([['picking_id','=',ppp.id]]).write({'location_id':ppp.picking_type_id.default_location_src_id.id})
				#ppp.move_ids_without_package.write({'location_dest_id':ppp.picking_type_id.default_location_dest_id.id})
				i=0
				for e in self.compatiblesLineas:
					ppp.move_ids_without_package[i].write({'location_id':ppp.picking_type_id.default_location_src_id.id,'location_dest_id':ppp.picking_type_id.default_location_dest_id.id,'product_id':e.serie.product_id.id,'x_studio_serie_destino':e.serie.id})
					#self.env['stock.move.line'].search([['picking_id','=',ppp.id]]).write({'location_id':almacen.lot_stock_id.id})
					#ppp.move_ids_without_package[i].write({'location_dest_id':ppp.picking_type_id.default_location_dest_id.id})
					i=i+1
			
			if('OUT' in ppp.name):
				ppp.write({'location_dest_id':ppp.picking_type_id.warehouse_id.lot_stock_id.id})
				#ppp.move_ids_without_package.write({'location_dest_id':ppp.picking_type_id.warehouse_id.lot_stock_id.id})
				#self.env['stock.move.line'].search([['picking_id','=',ppp.id]]).write({'location_dest_id':ppp.picking_type_id.warehouse_id.lot_stock_id.id})
				#ppp.move_ids_without_package.write({'location_id':ppp.picking_type_id.default_location_src_id.id})
				i=0
				for e in self.compatiblesLineas:
					ppp.move_ids_without_package[i].write({'location_dest_id':ppp.picking_type_id.default_location_dest_id.id,'product_id':e.serie.product_id.id,'x_studio_serie_destino':e.serie.id})
					#self.env['stock.move.line'].search([['picking_id','=',ppp.id]]).write({'location_id':almacen.lot_stock_id.id})
					#ppp.move_ids_without_package[i].write({'location_dest_id':ppp.picking_type_id.default_location_dest_id.id})
					i=i+1
			#ppp.action_confirm()
			#ppp.action_assign()