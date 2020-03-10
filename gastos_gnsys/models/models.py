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
    
    nombre = fields.Char(string="Nombre de gasto")
    
    quienSolcita     = fields.Many2one('res.users', string = "Quien solicita",track_visibility='onchange', default=lambda self: self.env.user)
    #quienSolcita     = fields.Char(string="Quien solicita?" ,track_visibility='onchange')
    proyecto = fields.Text(string="Proyecto", track_visibility='onchange')

    quienesAutorizan = fields.One2many('res.users', 'gastoAutoriza', string = "Responsable de autorizacion",track_visibility='onchange')
    quienesReciben   = fields.One2many('res.users', 'gastoRecibe', string = "Quien (es) reciben",track_visibility='onchange')

    montoRequerido   = fields.Float(string = 'Monto requerido',track_visibility='onchange')
    montoAprobado    = fields.Float(string = 'Monto aprobado',track_visibility='onchange')
    montoAtnticipado = fields.Float(string = 'Monto adelanto',track_visibility='onchange')
    
    formaDepagoAnticipo         = fields.Selection((('Efectivo','Efectivo'), ('Cheque','Cheque'),('Deposito','Deposito'),('Transferencia','Transferencia')), string = "Forma de pago",track_visibility='onchange')

    comoAplicaContablemente     = fields.Selection((('Opcion','Opcion'),('Opcion','Opcion'),('Opcion','Opcion')), string = "Como aplica contablemente",track_visibility='onchange')
    porCubrirAnticipo           = fields.Datetime(string = 'Fecha compromiso de adelanto', track_visibility='onchange')

    fechaPago                   = fields.Datetime(string = 'Fecha pago de adelanto',track_visibility='onchange')

    fechaLimiteDeComprobacion   = fields.Datetime(string = 'Fecha limite de comprobacion',track_visibility='onchange')


    anticipoCubierto            = fields.Float(string = 'Anticipo cubierto',track_visibility='onchange')

    #quienValida                 = fields.One2many('hr.employee', 'gastoValida', string = "Validado por",track_visibility='onchange')
    quienValida                 = fields.Char(string = "Responsable de aprobacion", track_visibility='onchange')

    motivos                     = fields.One2many('motivos', 'gasto', string = "Motivos",track_visibility='onchange')
    
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #Comprobo correctamentes
    comproboCorrectamente       = fields.Selection((('Exacto','Exacto'),('Parcial','Parcial'),('Excedido','Excedido')), string = "Tipo de comprobación",track_visibility='onchange')
    requiereDevolucion          = fields.Selection((('Efectivo','Efectivo'), ('Descuento nómina','Descuento nómina')), string = "Forma de pago",track_visibility='onchange')
    #Excacto
    montoExacto                 = fields.Float(string = 'Monto a cubrir',track_visibility='onchange')
    #Parcial
    montoParcial                = fields.Float(string = 'Monto a cubrir',track_visibility='onchange')
        #Parcial Efectivo
    aplicacionContaEfecParcial  = fields.Selection((('Opcion','Opcion'),('Opcion','Opcion'),('Opcion','Opcion')), string = "Como aplica contablemente",track_visibility='onchange')
    fechaLimDevEfecParcial      = fields.Datetime(string = 'Fecha límite devolución',track_visibility='onchange')
        #Parcial Nomina
    aplicacionContaNomParcial   = fields.Selection((('Opcion','Opcion'),('Opcion','Opcion'),('Opcion','Opcion')), string = "Como aplica contablemente",track_visibility='onchange')
    montoExtendido              = fields.Float(string = 'Monto a cubrir',track_visibility='onchange')
    #En caso de que la devolucion sea excendida
    formaDepago                 = fields.Selection((('La empresa cubre adicional','La empresa cubre adicional'), ('Receptor cubre adicional','Receptor cubre adicional')), string = "Forma de pago",track_visibility='onchange')
    #La empresa cubre lo adicional ¿La empresa cubre adicional? ¿Cuánto?
    #Forma en que caso de que la empresa cubra lo adicional
    formaDepagoExtendida    = fields.Selection((('Efectivo','Efectivo'), ('Cheque','Cheque'),('Depósito','Depósito'),('Transferencia','Transferencia')), string = "Forma de pago",track_visibility='onchange')

    fechaLimiteDePago       = fields.Datetime(string = 'Fecha límite de pago',track_visibility='onchange')
    fechaDePagoEmpresa      = fields.Datetime(string = 'Fecha de pago',track_visibility='onchange')
    fechaDePagoReceptor     = fields.Datetime(string = 'Fecha de pago',track_visibility='onchange')
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    montoCubrirAdicional    = fields.Float(string = 'Monto a cubrir donde el receptor cubre adicional',track_visibility='onchange')
    formaDeCobroAdicional   = fields.Selection((('Efectivo','Efectivo'), ('Descuento nómina','Descuento nómina')), string = "Forma de pago",track_visibility='onchange')
    #Si es por efectivo
    comoAplicaContablementeEfectivo    = fields.Selection((('Opcion','Opcion'),('Opcion','Opcion'),('Opcion','Opcion')), string = "Como aplica contablemente",track_visibility='onchange')
    fechaLimiteDeReceptor   = fields.Datetime(string = 'Fecha límite devolución',track_visibility='onchange')
    #Si es por descuento por nómina 
    comoAplicaContablementeReceptorCubreAdicional = fields.Selection((('Opcion','Opcion'),('Opcion','Opcion'),('Opcion','Opcion')), string = "Como aplica contablemente",track_visibility='onchange')
     #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #************************************************************
    tipoDevolucionSinComprobacion               = fields.Selection((('Efectivo','Efectivo'), ('Descuento nómina','Descuento nómina')), string = "Forma de pago",track_visibility='onchange')
    aplicacionContableDevolucionEfectivo        = fields.Selection((('Opcion','Opcion'),('Opcion','Opcion'),('Opcion','Opcion')), string = "Como aplica contablemente",track_visibility='onchange')
    fechaLimiteDevEfectivo                      = fields.Datetime(string = 'Fecha límite devolución',track_visibility='onchange')
    aplicacionContableDevolucionMonina          = fields.Selection((('Opcion','Opcion'),('Opcion','Opcion'),('Opcion','Opcion')), string = "Como aplica contablemente",track_visibility='onchange')
    #************************************************************
    etapas = fields.Many2one('gastos.etapa', string='Etapa', ondelete='restrict', track_visibility='onchange',readonly=True,copy=False,index=True)
    productos = fields.One2many('product.product','id',string='Solicitudes',store=True)
    

    comprobantes = fields.Many2many('ir.attachment', string="Comprobantes")

    tipoDeComprobacion = fields.Selection([('Exacto','Exacto'), ('Parcial','Parcial'), ('Excedido','Excedido'), ('noComprobado','No se comprobo correctamente')], string = "Tipo de comprobación", track_visibility='onchange')
    quienValidaMonto = fields.Char(string = "Gasto comprobado por", track_visibility='onchange')
    
    diasAtrasoPago = fields.Integer(compute='computarDiasAtrasoPago',string='Dias de atraso del pago')

    
    def computarDiasAtrasoPago(self):
        for rec in self:
            fecha = str(rec.create_date).split(' ')[0]
            converted_date = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
            rec.diasAtrasoPago = (datetime.date.today() - converted_date).days
    


    @api.multi
    def validarGasto(self):
        #_logger.info()
        gasto = self.env['gastos'].search([('id', '=', self.id)])        
        gasto.write({'x_studio_field_VU6DU': 'aprobado'
                     , 'quienValida': self.env.user.name
                   })

    @api.multi
    def validarComprobacion(self):
        message = ""
        mess = {}
        if str(self.tipoDeComprobacion) == "Exacto":
            if self.montoExacto < self.montoAprobado:
                raise exceptions.ValidationError("El gasto comprobado exacto no es igual al monto aprobado.")
                
                message = ("El gasto comprobado exacto no es igual al monto aprobado.")
                mess = {
                        'title': _('Gasto no comprobado!!!'),
                        'message' : message
                    }
                return {'warning': mess}

            else:
                gasto = self.env['gastos'].search([('id', '=', self.id)])        
                gasto.write({'x_studio_field_VU6DU': 'Comprobado'
                            , 'quienValidaMonto': self.env.user.name
                            })
                 
        elif str(self.tipoDeComprobacion) == "Parcial":
            _logger.info("Parcial")
        elif str(self.tipoDeComprobacion) == "Excedido":
            _logger.info("Excedido")
        elif str(self.tipoDeComprobacion) == "noComprobado":
            _logger.info("No comprobado")
        #else:
        #    pass

class motivos_gastos(models.Model):
    _name = 'motivos'
    _description = 'Motivos de un gasto'

    gasto  = fields.Many2one('gastos', string = "Gasto ", track_visibility='onchange')
    motivoDescripcion = fields.Text()
    tipoDeMotivo      = fields.Selection((('!','1'), ('2','2')), string = "Tipo de motivo",track_visibility='onchange')

class usuarios_gastos(models.Model):
    _inherit = 'res.users'
    gastoSolicitante = fields.One2many('gastos', 'quienSolcita', string="Gasto solicitante")
    gastoAutoriza = fields.Many2one('gastos', string="Gasto autoriza")
    gastoRecibe = fields.Many2one('gastos', string="Gasto autoriza")

class empleados_gastos(models.Model):
    _inherit = 'hr.employee'
    
    #gastoSolicitante = fields.One2many('gastos', 'quienSolcita', string="Gasto solicitante")
    #gastoValida = fields.Many2one('gastos', string="Gasto valida")
    
    
    
class gastosEtapas(models.Model):
    _name = 'gastos.etapa'
    _description = 'Etapas para los gastos'
    name = fields.Char(string='Nombre')
    
    sequence = fields.Integer(string="Secuencia")
    gasto = fields.One2many('gastos', 'etapas', string="Gasto")



