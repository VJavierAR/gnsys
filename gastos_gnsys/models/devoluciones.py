# -*- coding: utf-8 -*-

from odoo import _, models, fields, api, tools
from email.utils import formataddr
from odoo.exceptions import UserError
from odoo import exceptions, _
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)


class devoluciones(models.Model):
    _name = "gastos.pagoSolicitante"
    _description = 'Complemento/devolución'
    gasto = fields.Many2one('gastos', string="Gasto relacionado", track_visibility='onchange')


    #datos tabla compleneto/Devolucion
    montoEntregado = fields.Float(string = "Monto entregado")
    # montoJustificado = fields.Float(string = "Monto justificado")
    saldo = fields.Float(string = "Saldo", compute = "calcularSaldo", readonly = True)
    montoAjustado = fields.Float(string = "Monto ajustado")
    responsableDeMontoAjustado = fields.Many2one('res.users', string = "Responsable de monto ajustado", track_visibility='onchange')
    complementoDePagoPorHacer = fields.Float(string = "Complemento de pago por hacer")
    devolucionPorRecuperar = fields.Float(string = "Devolución por recuperar")


    # def calcularSaldo(self):
    #     for rec in self:
    #         rec.saldo = rec.montoEntregado - rec.montoJustificado
