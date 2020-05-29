# -*- coding: utf-8 -*-

from odoo import _, models, fields, api, tools
from email.utils import formataddr
from odoo.exceptions import UserError,RedirectWarning
from odoo import exceptions, _
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)


class HCliente(models.Model):
	_name = 'cliente.h'
	_description = 'Clientes de almacen'
	
	fecha = fields.Datetime(string = 'Fecha')

	origen = fields.Text(string = 'Origen')
	destino = fields.Text(string = 'Destino')
	localidad = fields.Text(string = 'Localidad')
	contadorBNPag = fields.Text(string = 'Contador BN Pag.')
	contadorColorPag = fields.Text(string = 'Contador Color Pag.')
	contadorBNML = fields.Text(string = 'Contador BN ML')
	contadorColorML = fields.Text(string = 'Contador Color ML')

	causa = fields.Text(string = 'Causa')

	serie = fields.Many2one('stock.production.lot', string = 'Serie')

class SeriesUpdate(models.Model):
	_inherit = 'stock.production.lot'

	clientes = fields.One2many('cliente.h', 'serie', string = 'Clientes', store = True)	