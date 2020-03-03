# -*- coding: utf-8 -*-

from odoo import _, models, fields, api, tools
from email.utils import formataddr
from odoo.exceptions import UserError
from odoo import exceptions, _
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)

class gastos_gnsys(models.Model):
    _name = 'gastos'
    _description = 'gastos_gnsys'

    quienSolcita     = fields.One2many('hr.employee', 'gastoSolicitante', string = "Quien solita",track_visibility='onchange')
    quienesAutorizan = fields.One2many('hr.employee' , string = "Quien (es) autorizan",track_visibility='onchange')
    quienesReciben   = fields.One2many('hr.employee' , string = "Quien (es) reciben",track_visibility='onchange')

    montoAprobado    = fields.float(string = 'Monto aprobado',track_visibility='onchange')
    montoAtnticipado = fields.float(string = 'Monto anticipo',track_visibility='onchange')


    formaDepago      = fields.selection((('Efectivo','Efectivo'), ('Cheque','Cheque'),('Depósito','Depósito'),('Transferencia','Transferencia')), string = "Forma de pago (Receptor)",track_visibility='onchange')


    comoAplicaContablemente     = fields.selection((('Opcion','Opcion'),('Opcion','Opcion'),('Opcion','Opcion')), string = "Como aplica contablemente",track_visibility='onchange')
    porCubrirAnticipo           = fields.datetime(string = 'Fecha límite de pago',track_visibility='onchange')

    fechaPago                   = fields.datetime(string = 'Fecha de pago',track_visibility='onchange')

    fechaLimiteDeComprobacion   = fields.datetime(string = 'Fecha límite de comprobación',track_visibility='onchange')


    anticipoCubierto            = fields.float(string = 'Anticipo cubierto',track_visibility='onchange')

    quienValida                 = fields.One2many('hr.employee', 'gastoValida', string = "Validado por",track_visibility='onchange')

    motivos                     = fields.One2many('motivos', 'gasto', string = "Motivos",track_visibility='onchange')


class motivos_gastos(models.Model):
    _name = 'motivos'
    _description = 'Motivos de un gasto'

    gasto  = fields.Many2one('gatos', string = "Gasto ", track_visibility='onchange')
    motivoDescripcion = fields.Text()
    tipoDeMotivo      = fields.selection((('!','1'), ('2','2')), string = "Tipo de motivo",track_visibility='onchange')

class empleados_gastos(models.Model):
    _inherit = 'hr.employee'
    
    gastoSolicitante = fields.Many2one('gastos', string="Gasto solicitante")
    gastoValida = fields.Many2one('gastos', string="Gasto valida")


        
