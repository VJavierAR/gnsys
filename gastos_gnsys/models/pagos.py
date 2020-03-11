# -*- coding: utf-8 -*-

from odoo import _, models, fields, api, tools
from email.utils import formataddr
from odoo.exceptions import UserError
from odoo import exceptions, _
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)

class pagos(models.Model):
    _name = 'gastos.pago'
    _description = 'Pagos de los gastos'
    gasto = fields.Many2one('gastos', string="Pago relacionado", track_visibility='onchange')

    #datos tabla pago de complemento/devolucion
    montoSolicitante = fields.Float(string = "Solicitante")
    montoEmpresa = fields.Float(string = "Empresa")
    concepto = fields.Text(string = "Concepto")
    formaDePago = fields.Selection((('Efectivo','Efectivo'), ('Cheque','Cheque'),('Deposito','Deposito'),('Transferencia','Transferencia')), string = "Forma de pago")
    fechaProgramada = fields.Datetime(string = 'Fecha programada')
    comprobanteDePago = fields.Many2many('ir.attachment', string="Comprobante de pago")
    montoPagado = fields.Float(string = "Monto pagado")
    fechaDePago = fields.Datetime(string = 'Fecha de pago')
    totalMonto = fields.Float(string = "Total de monto")

