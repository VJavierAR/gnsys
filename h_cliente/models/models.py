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
	active = fields.Boolean('Active', default=True, track_visibility=True)
	fecha = fields.Datetime(string = 'Fecha')
	fechaTexto = fields.Text(string = 'Fecha texto')
	origen = fields.Text(string = 'Origen')
	destino = fields.Text(string = 'Destino')
	localidadT = fields.Text(string = 'Localidad')
	contadorBNPag = fields.Text(string = 'Contador BN Pag.')
	contadorColorPag = fields.Text(string = 'Contador Color Pag.')
	contadorBNML = fields.Text(string = 'Contador BN ML')
	contadorColorML = fields.Text(string = 'Contador Color ML')
	causa = fields.Text(string = 'Causa')
	serie = fields.Many2one('stock.production.lot', string = 'Serie')
	contrato=fields.Many2one('contrato')
	servicio=fields.Many2one('servicios')
	localidad=fields.Many2one('res.partner')
	solicitud=fields.Many2one('sale.order')

class SeriesUpdate(models.Model):
	_inherit = 'stock.production.lot'
	clientes = fields.One2many('cliente.h', 'serie', string = 'Clientes', store = True)	
	clienteAnterior=fields.Boolean()
	localidadFacturacion=fields.Many2one('res.partner')
	active = fields.Boolean('Active', default=True, track_visibility=True)

	@api.onchange('clienteAnterior')
	def anterior(self):
		for record in self:
			clienteAn=record.cliente.search([[]],order='create_date desc')
			if record.clienteAnterior==False:
				if(len(clienteAn)>1):
					record['localidadFacturacion']=clienteAn[0].localidad.id
					record['servicio']=clienteAn[0].servicio.id

			
			if record.clienteAnterior:
				if(len(clienteAn)>1):
					record['localidadFacturacion']=clienteAn[1].localidad.id
					record['servicio']=clienteAn[1].servicio.id

