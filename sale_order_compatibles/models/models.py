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
	saleOrder = fields.Many2one('compatibles')
	equipos = fields.One2many('product.product', 'sale_order_compatibles_equipos', string = 'Equipos')
	componentes = fields.One2many('product.product', 'sale_order_compatibles_componentes', string = "Componentes")
	toner = fields.One2many('product.product', 'sale_order_compatibles_toner', string = "Toner")
	accesorios = fields.One2many('product.product', 'sale_order_compatibles_accesorios', string = "Accesorios")
	compatibles = fields.One2many('product.product', 'sale_order_compatibles_compatibles', string = "Compatibles")

	estado = fields.Selection(selection = [('1', '1'),('2', '2'),('3','3')], widget = "statusbar", default = '1')



class product_update(models.Model):
	_inherit = 'product.product'
	sale_order_compatibles_equipos = fields.Many2one('sale_order_compatibles')
	sale_order_compatibles_componentes = fields.Many2one('sale_order_compatibles')
	sale_order_compatibles_toner = fields.Many2one('sale_order_compatibles')
	sale_order_compatibles_accesorios = fields.Many2one('sale_order_compatibles')
	sale_order_compatibles_compatibles = fields.Many2one('sale_order_compatibles')


class sale_update(models.Model):
	_inherit = 'sale.order'
	compatiblesLineas = fields.One2many('sale_order_compatibles', 'saleOrder', string = 'nombre temp')


class sale_order_update(models.Model):
	_inherit = 'stock.production.lot'
	sale_order_compatibles = fields.Many2one('sale_order_compatibles')