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
	#componentes = fields.One2many('product.product', 'sale_order_compatibles_componentes', string = "Componentes")
	
	#toner = fields.Many2one('product.product', string = "Toner")
	#ccesorios = fields.Many2one('product.product', string = "Accesorios")
	#compatibles = fields.Many2one('product.product', string = "Compatibles")
	estado = fields.Selection(selection = [('1', '1'),('2', '2'),('3','3')], widget = "statusbar", default = '1')
	componentes = fields.One2many('sale_order_compatibles_mini', 'saleOrderMini', string = 'Componentes')



@api.onchange('equipos')
def filtroComponentes(self):
	dominio = {}

	#dominio = 

	#return res['domain'] = {'componentes':[('categ_id', '=', 5),('x_studio_toner_compatible.id','in',list)]}



class miniModelo(models.Model):
	_name = 'sale_order_compatibles_mini'
	idProducto = fields.Integer(string = 'id Producto')
	producto = fields.Many2one('product.product')
	cantidad = fields.Integer(string = 'Cantidad')
	saleOrderMini=fields.Many2one('sale_order_compatibles')
		




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