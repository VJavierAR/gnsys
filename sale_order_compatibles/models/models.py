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
	cantidad = fields.Integer(string = 'Cantidad')
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
		da=self.env['product.product'].browse(eval(self.idProducto)).filtered(lambda x:x.categ_id.id==11).mapped('id')
		res['domain']={'producto':[['id','in',da]]}
		return res


	
	"""
	@api.onchange('idProducto')
	def dominioProducto(self):
		dominio = [('categ_id', '=', self.idProducto)]
		res['domain'] = {'producto': dominio}
		return res
	"""




# class product_update(models.Model):
# 	_inherit = 'product.product'
# 	sale_order_compatibles_equipos = fields.Many2one('sale_order_compatibles')
# 	sale_order_compatibles_componentes = fields.Many2one('sale_order_compatibles')


# 	sale_order_compatibles_toner = fields.One2many('sale_order_compatibles', 'toner')
# 	sale_order_compatibles_accesorios = fields.One2many('sale_order_compatibles', 'accesorios')
# 	sale_order_compatibles_compatibles = fields.One2many('sale_order_compatibles', 'compatibles')

# 	sale_order_compatibles_mini_producto = fields.One2many('sale_order_compatibles_mini', 'producto')


class sale_update(models.Model):
	_inherit = 'sale.order'
	compatiblesLineas = fields.One2many('sale_order_compatibles', 'saleOrder', string = 'nombre temp')


# class sale_order_update(models.Model):
# 	_inherit = 'stock.production.lot'
# 	sale_order_compatibles = fields.Many2one('sale_order_compatibles')