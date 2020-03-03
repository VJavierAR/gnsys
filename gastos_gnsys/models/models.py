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
    #xd
    quienSolcita     = fields.Many2one('hr.employee', string = "Quien solita",track_visibility='onchange')
    quienesAutorizan = fields.One2many('hr.employee', 'gastoAutoriza', string = "Quien (es) autorizan",track_visibility='onchange')
    quienesReciben   = fields.One2many('hr.employee', 'gastoRecibe', string = "Quien (es) reciben",track_visibility='onchange')

    montoAprobado    = fields.Float(string = 'Monto aprobado',track_visibility='onchange')
    montoAtnticipado = fields.Float(string = 'Monto anticipo',track_visibility='onchange')


    formaDepagoAnticipo         = fields.Selection((('Efectivo','Efectivo'), ('Cheque','Cheque'),('Depósito','Depósito'),('Transferencia','Transferencia')), string = "Forma de pago (Receptor)",track_visibility='onchange')


    comoAplicaContablemente     = fields.Selection((('Opcion','Opcion'),('Opcion','Opcion'),('Opcion','Opcion')), string = "Como aplica contablemente",track_visibility='onchange')
    porCubrirAnticipo           = fields.Datetime(string = 'Fecha límite de pago',track_visibility='onchange')

    fechaPago                   = fields.Datetime(string = 'Fecha de pago',track_visibility='onchange')

    fechaLimiteDeComprobacion   = fields.Datetime(string = 'Fecha límite de comprobación',track_visibility='onchange')


    anticipoCubierto            = fields.Float(string = 'Anticipo cubierto',track_visibility='onchange')

    quienValida                 = fields.One2many('hr.employee', 'gastoValida', string = "Validado por",track_visibility='onchange')

    motivos                     = fields.One2many('motivos', 'gasto', string = "Motivos",track_visibility='onchange')
    
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    comproboCorrectamente       = fields.Selection((('Exacto','Exacto'),('Parcial','Parcial'),('Excedido','Excedido')), string = "Tipo de comprobación",track_visibility='onchange')

    requiereDevolucion          = fields.Selection((('Efectivo','Efectivo'),('Descuento nómina','Descuento nómina')), string = "¿Requiere devolución?",track_visibility='onchange')

    #En caso de que sea por efectivo o excacto
    #Parcial
    monto                       = fields.Float(string = 'Monto a cubrir',track_visibility='onchange')
    #En caso de que sea por efectivo o por nomina
    comoAplicaContablementeRequerimeintoDevolucion  = fields.Selection((('Opcion','Opcion'),('Opcion','Opcion'),('Opcion','Opcion')), string = "Como aplica contablemente",track_visibility='onchange')


    #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    #En caso de que la devolucion sea excendida

    formaDepago = fields.Selection((('¿La empresa cubre adicional? ¿Cuánto?','¿La empresa cubre adicional? ¿Cuánto?'), ('¿Receptor cubre adicional?','¿Receptor cubre adicional?')), string = "Forma de pago (Receptor)",track_visibility='onchange')
    #La empresa cubre lo adicional ¿La empresa cubre adicional? ¿Cuánto?
    #Forma en que caso de que la empresa cubra lo adicional
    formaDepagoExtendida    = fields.Selection((('Efectivo','Efectivo'), ('Cheque','Cheque'),('Depósito','Depósito'),('Transferencia','Transferencia')), string = "Forma de pago (Receptor)",track_visibility='onchange')

    fechaLimiteDePago       = fields.Datetime(string = 'Fecha límite de pago',track_visibility='onchange')
    fechaDePago             = fields.Datetime(string = 'De pago',track_visibility='onchange')


    #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    montoCubrirAdicional    = fields.Float(string = 'Monto a cubrir donde el receptor cubre adicional',track_visibility='onchange')

    formaDeCobroAdicional   = fields.Selection((('Efectivo','Efectivo'), ('Descuento nómina','Descuento nómina')), string = "Forma de pago (Receptor)",track_visibility='onchange')

    #Si es por efectivo
    comoAplicaContablementeEfectivo    = fields.Selection((('Opcion','Opcion'),('Opcion','Opcion'),('Opcion','Opcion')), string = "Como aplica contablemente",track_visibility='onchange')

    fechaLimiteDeReceptor   = fields.Datetime(string = 'Fecha límite devolución',track_visibility='onchange')

    #Si es por descuento por nómina 
    comoAplicaContablementeReceptorCubreAdicional = fields.Selection((('Opcion','Opcion'),('Opcion','Opcion'),('Opcion','Opcion')), string = "Como aplica contablemente",track_visibility='onchange')


class motivos_gastos(models.Model):
    _name = 'motivos'
    _description = 'Motivos de un gasto'

    gasto  = fields.Many2one('gatos', string = "Gasto ", track_visibility='onchange')
    motivoDescripcion = fields.Text()
    tipoDeMotivo      = fields.Selection((('!','1'), ('2','2')), string = "Tipo de motivo",track_visibility='onchange')

class empleados_gastos(models.Model):
    _inherit = 'hr.employee'
    
    gastoSolicitante = fields.One2many('gastos', 'quienSolcita', string="Gasto solicitante")
    gastoValida = fields.Many2one('gastos', string="Gasto valida")
    
    gastoAutoriza = fields.Many2one('gastos', string="Gasto autoriza")
    gastoRecibe = fields.Many2one('gastos', string="Gasto autoriza")

        
