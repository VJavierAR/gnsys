# -*- coding: utf-8 -*-

from odoo import _, models, fields, api, tools
from email.utils import formataddr
from odoo.exceptions import UserError
from odoo import exceptions, _
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)


class Pagos(models.Model):
    _name = 'gastos.pago'
    _description = 'Pagos de los gastos'
    gasto = fields.Many2one('gastos', string="Pago relacionado", track_visibility='onchange')
    # -------Usuario------------
    concepto = fields.Text(string = "Concepto", track_visibility='onchange')
    fechaDePago = fields.Datetime(string = 'Fecha de pago', track_visibility='onchange')
    montoPagado = fields.Float(string = "Monto de pago", track_visibility='onchange')
    formaDePago = fields.Selection((('Efectivo','Efectivo'), ('Cheque','Cheque'),('Deposito','Deposito'),('Transferencia','Transferencia')), string = "Forma de pago")
    comprobanteDePago = fields.Many2many('ir.attachment', string="Evidencia")
    # -----------------------
    #datos tabla pago de complemento/devolucion
    montoSolicitante = fields.Float(string = "Solicitante")
    montoEmpresa = fields.Float(string = "Empresa")
    fechaProgramada = fields.Datetime(string = 'Fecha programada')
    totalMonto = fields.Float(string = "Total de monto")

