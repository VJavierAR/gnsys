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
    #quienesAutorizan = fields.One2many('res.users', 'gastoAutoriza', string = "Responsable de autorizacion",track_visibility='onchange')
    #quienesAutorizan = fields.Char(string = "Responsable de autorizacion", track_visibility='onchange')
    quienesAutorizan = fields.Many2one('res.users',string = "Responsable de autorizacion", track_visibility='onchange', default=lambda self: self.env.user)
    quienesReciben   = fields.One2many('res.users', 'gastoRecibe', string = "Quien (es) reciben",track_visibility='onchange')
    montoAprobado   = fields.Float(string = 'Monto aprobado',track_visibility='onchange')
    montoRequerido   = fields.Float(string = 'Monto requerido',track_visibility='onchange')
    montoAdelantado = fields.Float(string = 'Monto adelanto',track_visibility='onchange')
    montoAtnticipado = fields.Float(string = 'Monto anticipo',track_visibility='onchange')
    autorizacionLider = fields.Selection([('Aprobada','Aprobada'), ('Rechazada','Rechazada')], string = "Autorización", track_visibility='onchange')
    autorizacionFinanzas = fields.Selection([('Aprobada','Aprobada'), ('Rechazada','Rechazada')], string = "Autorización", track_visibility='onchange')
    proyecto = fields.Text(string="Proyecto", track_visibility='onchange')
    fechaLimitePagoGasto = fields.Datetime(string = 'Fecha limite de pago', track_visibility='onchange')
    fechaLimiteComprobacionFinanzas = fields.Datetime(string = 'Fecha limite de comprobacion',track_visibility='onchange')

    formaDepagoAnticipo         = fields.Selection((('Efectivo','Efectivo'), ('Cheque','Cheque'),('Deposito','Deposito'),('Transferencia','Transferencia')), string = "Forma de pago",track_visibility='onchange')

     

    comoAplicaContablemente     = fields.Selection((('Opcion','Opcion'),('Opcion','Opcion'),('Opcion','Opcion')), string = "Como aplica contablemente",track_visibility='onchange')
    porCubrirAnticipo           = fields.Datetime(string = 'Fecha compromiso de adelanto', track_visibility='onchange')

    fechaPago                   = fields.Datetime(string = 'Fecha pago de adelanto',track_visibility='onchange')

    fechaLimiteDeComprobacion   = fields.Datetime(string = 'Fecha limite de comprobacion',track_visibility='onchange')


    anticipoCubierto            = fields.Float(string = 'Anticipo cubierto',track_visibility='onchange')

    #quienValida                 = fields.One2many('hr.employee', 'gastoValida', string = "Validado por",track_visibility='onchange')
    quienValida                 = fields.Many2one('res.users',string = "Responsable de aprobacion", track_visibility='onchange', default=lambda self: self.env.user)

    motivos                     = fields.One2many('motivos', 'gasto', string = "Motivos",track_visibility='onchange')
    totalMontoMotivos = fields.Float(string = 'Total',track_visibility='onchange')
    
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

    fechaLimite             = fields.Datetime(string = 'Fecha límite', track_visibility = 'onchange')
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
    
    comprobantes        = fields.Many2many('ir.attachment', string="Comprobantes")
    

    tipoDeComprobacion = fields.Selection([('Exacto','Exacto'), ('Parcial','Parcial'), ('Excedido','Excedido'), ('noComprobado','No se comprobo correctamente')], string = "Tipo de comprobación", track_visibility='onchange')
    quienValidaMonto = fields.Char(string = "Gasto comprobado por", track_visibility='onchange')
    
    diasAtrasoPago = fields.Integer(compute='computarDiasAtrasoPago',string='Dias de atraso del pago')



    #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$4

    comprobaciones = fields.One2many('gastos.comprobaciones', 'comprobante', string = "Comprobantes",track_visibility='onchange')
    montoPagadoComprobado = fields.Float(string = "Monto pagado", track_visibility='onchange')
    montoComprobado = fields.Float(string = "Monto comprobado", track_visibility='onchange')
    montoComprobadoAprobado =  fields.Float(string = "Monto comprobado aprobado", track_visibility='onchange')
    # --------------------
    devoluciones = fields.One2many('gastos.devolucion', 'gasto' , string = 'Devoluciones', track_visibility = 'onchange')
    totalPagosSolitantes = fields.Float(string = "Total monto pagado", track_visibility='onchange')

    @api.onchange('devoluciones')
    def calcularTotalPagoDevolucion(self):
        listaDevoluciones = self.devoluciones
        montoPagadoTotal = 0.0
        if listaDevoluciones != []:
            for devolucion in listaDevoluciones:
                montoPagadoTotal += devolucion.montoEntregado
        self.totalPagosSolitantes = montoPagadoTotal
    # --------------------
    #Modelo de devoluciónes
    pagos = fields.One2many('gastos.pago', 'gasto' , string = 'Pagos', track_visibility = 'onchange')    
    
    montoComprobadoPago = fields.Float(string = "Monto comprobado", track_visibility='onchange')
    montoComprobadoAprobadoPago = fields.Float(string = "Monto comprobado aprobado", track_visibility='onchange')
    montoPagadoOriPago = fields.Float(string = "Monto de pago", track_visibility='onchange')
    montoADevolverPago = fields.Float(string = "Monto a devolver", track_visibility='onchange')
    montoDevueltoPago = fields.Float(string = "Monto devuelto", track_visibility='onchange')
    


    totalDeMontoPagado = fields.Float(string = 'Total')

    # @api.onchange('devoluciones')
    # def calcularTotalPagoDevolucion(self):
    #     listaDevoluciones = self.devoluciones
    #     montoPagadoTotal = 0.0
    #     if listaDevoluciones != []:
    #         for devolucion in listaDevoluciones:
    #             montoPagadoTotal += devolucion.montoPagado
    #     self.totalDeMontoPagado = montoPagadoTotal

    
    def computarDiasAtrasoPago(self):
        for rec in self:
            fecha = str(rec.create_date).split(' ')[0]
            converted_date = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
            rec.diasAtrasoPago = (datetime.date.today() - converted_date).days
    

    @api.multi
    def autorizarGasto(self):
        gasto = self.env['gastos'].search([('id', '=', self.id)])
        gasto.write({'quienesAutorizan': self.env.user.name})

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





class usuarios_gastos(models.Model):
    _inherit = 'res.users'
    gastoSolicitante = fields.One2many('gastos', 'quienSolcita', string="Gasto solicitante")
    gastoAtoriza = fields.One2many('gastos', 'quienesAutorizan', string="Gasto autorizo")
    gastoAutoriza = fields.Many2one('gastos', string="Gasto autoriza")
    gastoAprobacion = fields.One2many('gastos', 'quienValida', string="Gasto aprobación")

    gastoRecibe = fields.Many2one('gastos', string="Gasto autoriza")
    devoResponsableAjuste = fields.Text(string = "Devolucion responsable",track_visibility='onchange')
    pagoSolicitanteAutoriza = fields.One2many('gastos.devolucion','quienesReciben' ,string="Pago autoriza")
    #devoResponsableAjuste = fields.One2many('gastos.devolucion', 'responsableDeMontoAjustado', string = "Devolucion responsable")

class cliente_comprobante(object):
    _inherit = 'res.partner'
    comprobacion = fields.One2many('gastos.comprobaciones', 'cliente', string = "Comprobación")
        


class gastosEtapas(models.Model):
    _name = 'gastos.etapa'
    _description = 'Etapas para los gastos'
    name = fields.Char(string='Nombre')
    
    sequence = fields.Integer(string="Secuencia")
    gasto = fields.One2many('gastos', 'etapas', string="Gasto")



class motivos_gastos(models.Model):
    _name = 'motivos'
    _description = 'Motivos de un gasto'

    gasto  = fields.Many2one('gastos', string = "Gasto ", track_visibility='onchange')
    #motivoDescripcion = fields.Text()
    #tipoDeMotivo      = fields.Selection((('!','1'), ('2','2')), string = "Tipo de motivo",track_visibility='onchange')

    motivoDescripcion = fields.Text(string = "Descripción de gasto",track_visibility='onchange')
    motivoNumeroTicket = fields.Text(string = "Número de ticket",track_visibility='onchange')
    motivoConcepto = fields.Text(string = "Motivo (Concepto)",track_visibility='onchange')
    motivoCentroCostos = fields.Text(string = "Centro de costos",track_visibility='onchange')
    motivoTipoDeMotivo      = fields.Selection((('!','1'), ('2','2')), string = "Tipo de motivo",track_visibility='onchange')
    monto = fields.Float(string = "Monto", track_visibility='onchange')


class comprobaciones(models.Model):
    _name = 'gastos.comprobaciones'
    _description = 'Tipos de comprobaciónes del gasto'
    comprobante             = fields.Many2one('gastos', string = "Comprobación ", track_visibility='onchange')

    # -------Usuario------------
    concepto                = fields.Text(string = "Concepto",      track_visibility='onchange')
    descripcion             = fields.Text(string = "Descripción",   track_visibility='onchange')
    justificacon            = fields.Text(string = "Justificación", track_visibility='onchange')
    tipoDeComprobante       = fields.Selection((('Factura','Factura'),('FacturaSinIva','Factura sin IVA'),('TiketFacturable','Ticket facturable'),('Tiket','Ticket'),('Nota','Nota')), string = "Tipo de Comprobante",track_visibility='onchange')
    comprobantes            = fields.Many2many('ir.attachment', string="Comprobantes")
    # -------Finanzas------------
    porcentajeAceptado      = fields.Selection((('100','100%'),('75','75%'),('50','50%'),('25','25%'),('0','0%')), string = "Porcentaje Aceptado",track_visibility='onchange')
    cuentaContableDestino   = fields.Text(string = "Aplicación contable", track_visibility='onchange')
    montoAprobadooriginalMante = fields.Float(string = "Monto aprobado originalmente", track_visibility='onchange')
    #----------------------------
    monto                   = fields.Float(string = "Monto",         track_visibility='onchange')
    nombre                  = fields.Char(string="Nombre de comprobación", track_visibility='onchange')
    montoJustificado        = fields.Float(string = 'Monto aprobado', compute='calcularMontoAprobado', track_visibility='onchange')
    
    centoDeCostos           = fields.Text(string = "Centro de Costos", track_visibility='onchange')
    cliente = fields.Many2one('res.partner', string = 'Cliente', track_visibility='onchange')
    servicio = fields.Text(string = 'Servicio')

    def calcularMontoAprobado(self):
        for rec in self:
            if str(rec.porcentajeAceptado) != 'false':
                montoJustificado = rec.monto * rec.porcentajeAceptado


class PagoSolicitante(models.Model):
    _name = "gastos.devolucion"
    #_description = 'Complemento/devolución'
    _description = 'Pago a solicitante'
    gasto = fields.Many2one('gastos', string="Pagos solitatados", track_visibility='onchange')
    quienesReciben = fields.Many2one('res.users',string = "Quien recibe", track_visibility='onchange', default=lambda self: self.env.user)

    #datos tabla compleneto/Devolucion
    montoEntregado = fields.Float(string = "Monto")
    fecha = fields.Datetime(string = 'Fecha', track_visibility = 'onchange')
    formaDePago = fields.Selection((('Efectivo','Efectivo'), ('Cheque','Cheque'),('Deposito','Deposito'),('Transferencia','Transferencia')), string = "Forma de pago")
    fechaLimite = fields.Datetime(string = 'Fecha límite comprobación', track_visibility = 'onchange')
    evidencia = fields.Many2many('ir.attachment', string="Evidencia")
    montoAprobadoOriginalMante  = fields.Float(string = "Monto aprobado originalmente", track_visibility='onchange')
    montoPagado = fields.Float(string = "Monto pagado")
    # montoJustificado = fields.Float(string = "Monto justificado")
    # saldo = fields.Float(string = "Saldo", compute = "calcularSaldo", readonly = True)
    # montoAjustado = fields.Float(string = "Monto ajustado")
    # responsableDeMontoAjustado = fields.Many2one('res.users', string = "Responsable de monto ajustado", track_visibility='onchange')
    # complementoDePagoPorHacer = fields.Float(string = "Complemento de pago por hacer")
    # devolucionPorRecuperar = fields.Float(string = "Devolución por recuperar")
    # def calcularSaldo(self):
    #     for rec in self:
    #         rec.saldo = rec.montoEntregado - rec.montoJustificado

class pagos(models.Model):
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

