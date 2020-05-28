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
	cantidad = fields.Integer(string = 'Cantidad',default=1,readonly=True)
	estado = fields.Selection(selection = [('1', '1'),('2', '2'),('3','3')], widget = "statusbar", default = '1')
	componentes = fields.One2many('sale_order_compatibles_mini', 'saleOrderMini', string = 'Componentes')
	toner = fields.One2many('sale_order_compatibles_mini_toner', 'saleOrderMini', string = 'Toner')
	accesorios = fields.One2many('sale_order_compatibles_mini_acesorios', 'saleOrderMini', string = 'Accesorios')
	domin=fields.Char()

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

	@api.onchange('idProducto')
	def domi(self):
		res={}
		if(self.idProducto and self.idProducto!='[]'):
			da=self.env['product.product'].browse(eval(self.idProducto)).filtered(lambda x:x.categ_id.id==11).mapped('id')
			res['domain']={'producto':[['id','in',da]]}
		return res

class sale_update(models.Model):
	_inherit = 'sale.order'
	compatiblesLineas = fields.One2many('sale_order_compatibles', 'saleOrder', string = 'nombre temp')


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
		data=[]
		if(len(self.compatiblesLineas)>0):
			for e in self.compatiblesLineas:
				d={'product_id':e.equipos.id,'name':e.equipos.name,'product_uom_qty':1,'product_uom':e.equipos.uom_id.id,'price_unit':0.00,'x_studio_id_relacion':e.id}
				data.append(d)
				for e1 in e.componentes:
					d={'product_id':e1.producto.id,'name':e1.producto.name,'product_uom_qty':e1.cantidad,'product_uom':e1.producto.uom_id.id,'price_unit':0.00,'x_studio_id_relacion':e.id,'x_studio_modelo':e.equipos.name}
					data.append(d)
				for e2 in e.toner:
					d={'product_id':e2.producto.id,'name':e2.producto.name,'product_uom_qty':e2.cantidad,'product_uom':e2.producto.uom_id.id,'price_unit':0.00,'x_studio_id_relacion':e.id,'x_studio_modelo':e.equipos.name}
					data.append(d)
				for e3 in e.accesorios:
					d={'product_id':e3.producto.id,'name':e3.producto.name,'product_uom_qty':e3.cantidad,'product_uom':e3.producto.uom_id.id,'price_unit':0.00,'x_studio_id_relacion':e.id,'x_studio_modelo':e.equipos.name}
					data.append(d)
			self.order_line=data