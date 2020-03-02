# -*- coding: utf-8 -*-

from odoo import _, models, fields, api, tools
from email.utils import formataddr
from odoo.exceptions import UserError
from odoo import exceptions, _
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)

class servicios_gnsys(models.Model):
    _name = 'servicios'
    _description = 'Servicios GNSYS'

    productos = fields.One2many('product.product', 'servicio', string="Productos")
    
    descripcion = fields.Text(string="Descripción")
    rentaMensual = fields.Text(string="Renta mensual")

    bolsaBN = fields.Integer(string="Bolsa B/N")
    clickExcedenteBN = fields.Integer(string="Click excedente B/N")
    procesadoBN = fields.Integer(string="Procesado B/N")

    bolsaColor = fields.Integer(string="Bolsa color")
    clickExcedenteColor = fields.Integer(string="Click excedente color")
    procesadoColor = fields.Integer(string="Procesado color")
    
    series = fields.One2many('stock.production.lot', 'servicio', string="Series")
    
    color_bn = fields.Integer(string="Color - B/N")

    lecAntBN = fields.Integer(string="Lectura anterior B/N")
    lecActualBN = fields.Integer(string="Lectura actual B/N")
    procesadoBN = fields.Integer(string="Procesado B/N")

    lecAntColor = fields.Integer(string="Lectura anterior color")
    lecActualColor = fields.Integer(string="Lectura actual color")
    procesadoColor = fields.Integer(string="Procesado color")

    modelo = fields.Text(string="Modelo")
    
    contrato = fields.Many2one('contrato', string="Contrato")
    
class productos_en_servicios(models.Model):
    _inherit = 'product.product'
    servicio = fields.Many2one('servicios', string="Servicio producto")
    
class equipo_series(models.Model):
    _inherit = 'stock.production.lot'
    servicio = fields.Many2one('servicios', string="Servicio serie")

class contratos(models.Model):
    _name = "contrato"
    _description = 'Contratos GNSYS'
    
    servicio = fields.One2many('servicios', 'contrato', string="Servicio")
    
