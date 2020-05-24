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
	equipos = fields.One2many('stock.production.lot', 'sale_order_compatibles', string = 'Equipos')
	componentes = fields.Many2many('product.product', string = "Componentes")
	toner = fields.Many2many('product.product', string = "Toner")
	compatibles = fields.Many2many('product.product', string = "Compatibles")



class sale_order_update(models.Model):
	_inherit = 'stock.production.lot'
	sale_order_compatibles = fields.Many2one('sale_order_compatibles')

class sale_update(models.Model):
	_inherit = 'sale.order'
	compatiblesLineas = fields.One2many('sale_order_compatibles', 'saleOrder', string = 'nombre temp')
