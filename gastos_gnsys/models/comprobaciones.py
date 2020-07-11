# -*- coding: utf-8 -*-

from odoo import _, models, fields, api, tools
from email.utils import formataddr
from odoo.exceptions import UserError
from odoo import exceptions, _
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)

class comprobaciones(models.Model):
    _name = 'gastos.comprobaciones'
    _description = 'Tipos de comprobaciónes del gasto'
    nombre                  = fields.Char(string="Nombre de comprobación", track_visibility='onchange')
    comprobante             = fields.Many2one('gastos', string = "Comprobación ", track_visibility='onchange')
    concepto                = fields.Text(string = "Concepto",      track_visibility='onchange')
    descripcion             = fields.Text(string = "Descripción",   track_visibility='onchange')
    justificacon            = fields.Text(string = "Justificación", track_visibility='onchange')
    monto                   = fields.Float(string = "Monto",         track_visibility='onchange')
    comprobantes            = fields.Many2many('ir.attachment', string="Comprobantes")
    tipoDeComprobante       = fields.Selection((('Factura','Factura'),('FacturaSinIva','Factura sin IVA'),('TiketFacturable','Ticket facturable'),('Tiket','Ticket'),('Nota','Nota')), string = "Tipo de Comprobante",track_visibility='onchange')
    porcentajeAceptado      = fields.Selection((('100','100%'),('75','75%'),('50','50%'),('25','25%'),('0','0%')), string = "Porcentaje Aceptado",track_visibility='onchange')
    # montoJustificado        = fields.Float(string = 'Monto aprobado', compute='calcularMontoAprobado', track_visibility='onchange')
    cuentaContableDestino   = fields.Text(string = "Aplicación contable", track_visibility='onchange')
    centoDeCostos           = fields.Text(string = "Centro de Costos", track_visibility='onchange')
    cliente = fields.Many2one('res.partner', string = 'Cliente', track_visibility='onchange')
    servicio = fields.Text(string = 'Servicio')

    # def calcularMontoAprobado(self):
    #     for rec in self:
    #         if str(rec.porcentajeAceptado) != 'false':
    #             montoJustificado = rec.monto * rec.porcentajeAceptado