# -*- coding: utf-8 -*-

from odoo import _, models, fields, api, tools
from email.utils import formataddr
from odoo.exceptions import UserError
from odoo import exceptions, _
import logging, ast
import datetime, time
import xml.etree.ElementTree as ET
import base64
from io import BytesIO as StringIO
from odoo.tools.mimetypes import guess_mimetype
from xml.dom import minidom

_logger = logging.getLogger(__name__)



try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

try:
    from . import odf_ods_reader
except ImportError:
    odf_ods_reader = None

FILE_TYPE_DICT = {
    'text/csv': ('csv', True, None),
    'application/vnd.ms-excel': ('xls', xlrd, 'xlrd'),
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ('xlsx', xlsx, 'xlrd >= 1.0.0'),
    'application/vnd.oasis.opendocument.spreadsheet': ('ods', odf_ods_reader, 'odfpy')
}
EXTENSIONS = {
    '.' + ext: handler
    for mime, (ext, handler, req) in FILE_TYPE_DICT.items()
}



class gastos_gnsys(models.Model):
    _name = 'gastos'
    _description = 'gastos_gnsys'
    # --- NOMBRE DEL GASTO | USUARIO FINAL ---
    nombre = fields.Char(string="Nombre de gasto", track_visibility='onchange')
    statusGasto = fields.Selection([('enSolicitud','EN SOLICITUD'), ('autorizacion','GASTO AUTORIZADO'), ('aprovacion','GASTO APROBADO'), ('cancelado','Cancelado')], required = True, default='enSolicitud', string = "Status de gasto")
    # --- SOLICITUD | USUARIO FINAL ---
    quienSolcita = fields.Many2one('res.users', string = "Quien solicita",track_visibility='onchange', default=lambda self: self.env.user)
    proyecto = fields.Text(string="Proyecto", track_visibility='onchange')




    proyecto_select = fields.Selection([('Proyecto1','Proyecto 1'),('Proyecto2','Proyecto 2'),('Proyecto3','Proyecto 3')], string = "Escoge el proyecto", track_visibility='onchange')
    




    montoRequerido = fields.Float(string = 'Monto requerido',track_visibility='onchange')
    fechaDeSolicitud = fields.Datetime(compute='computarfechaDeSolicitud',string = 'Fecha de solicitud', track_visibility='onchange')
    fechaLimite = fields.Datetime(string = 'Fecha limite de pago', track_visibility='onchange')
    def computarfechaDeSolicitud(self):
        for rec in self:
            fecha = str(rec.create_date).split(' ')[0]
            converted_date = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
            self.fechaDeSolicitud = converted_date 
    # --- AUTORIZACIÓN | LÍDER (PUEDE SER MULTIPLE)
    quienesAutorizan = fields.Many2one('res.users',string = "Responsable de autorizacion", track_visibility='onchange', default=lambda self: self.env.user)
    autorizacionLider = fields.Selection([('aprobado','El gasto esta autoriazado'), ('rechazado','El gasto esta rechazado'),('enEspera','En espera')], default='enEspera',string = "Autorización", track_visibility='onchange')
    montoAutorizado = fields.Float(string = 'Monto autorizado',track_visibility='onchange')
    @api.onchange('montoRequerido')
    def definirMontoAutorizado(self):
        if self.montoRequerido :
            if not self.montoAutorizado :    
                self.montoAutorizado = self.montoRequerido
    # --- APROBACIÓN | FINANSAS
    quienValida = fields.Many2one('res.users',string = "Responsable de aprobacion", track_visibility='onchange', default=lambda self: self.env.user)
    montoAprobadoFinal = fields.Float(string = 'Monto aprobado',track_visibility='onchange')
    montoAnticipado = fields.Float(string = 'Monto anticipo',track_visibility='onchange')
    porCubrirAnticipo = fields.Datetime(string = 'Fecha compromiso de adelanto', track_visibility='onchange')
    autorizacionFinanzas = fields.Selection([('aprobado','El gasto esta aprobado'), ('rechazado','El gasto esta rechazado'),('enEspera','En espera')], default='enEspera', string = "Autorización", track_visibility='onchange')
    fechaLimiteComprobacionFinanzas = fields.Datetime(string = 'Fecha limite de comprobacion',track_visibility='onchange')
    @api.onchange('porCubrirAnticipo')
    def mensajeEsMayorFechaLimite(self):
        if self.porCubrirAnticipo :
            if self.fechaLimite:
                fechaCompleta = str(self.porCubrirAnticipo).split(' ')[0]
                fechaCompleta = fechaCompleta.split('-')

                fecha1 = datetime.datetime(int(fechaCompleta[0]), int(fechaCompleta[1]), int(fechaCompleta[2]))
                
                fechaHoy = str(self.fechaLimite).split(' ')[0]
                fechaHoy = fechaHoy.split('-')

                fecha2 = datetime.datetime(int(fechaHoy[0]), int(fechaHoy[1]), int(fechaHoy[2]))
                message = ""
                mess = {}
                esMenor = "Es menor"
                esMayor = "Es mayor"
                if fecha1 < fecha2 :
                    _logger.info("||||-:   "+esMayor)
                else:
                    return { 'warning': { 'title': 'Mensaje de aviso ', 'message': 'La fecha de compromiso de adelanto es mayor a la fecha limite, usted puede continuar'} }
    @api.onchange('fechaLimiteComprobacionFinanzas')
    def mensajeIgualFechaAdelanto(self):
        if self.fechaLimiteComprobacionFinanzas :
            if self.porCubrirAnticipo:
                fechaCompleta = str(self.fechaLimiteComprobacionFinanzas).split(' ')[0]
                fechaCompleta = fechaCompleta.split('-')

                fecha1 = datetime.datetime(int(fechaCompleta[0]), int(fechaCompleta[1]), int(fechaCompleta[2]))
                
                fechaHoy = str(self.porCubrirAnticipo).split(' ')[0]
                fechaHoy = fechaHoy.split('-')

                fecha2 = datetime.datetime(int(fechaHoy[0]), int(fechaHoy[1]), int(fechaHoy[2]))
                message = ""
                mess = {}
                if fecha1 == fecha2 :
                    return { 'warning': { 'title': 'Mensaje de aviso ', 'message': 'La fecha de compromiso de adelanto es igual a la fecha limite de comprobacion, usted puede continuar'} }
    # --- FUNCION PARA VERFICAR QUE LA FECHA NO ES MENOR AL DÍA DE HOY
    @api.constrains('fechaLimite', 'porCubrirAnticipo','fechaLimiteComprobacionFinanzas')
    def calculaFechaLimite(self):
        fechaHoy = datetime.date.today()
        fechaHoy = str(fechaHoy)
        fechaHoy = fechaHoy.split('-')
        fecha2 = datetime.datetime(int(fechaHoy[0]), int(fechaHoy[1]), int(fechaHoy[2]))
        message = ""
        mess = {}
        esMenor = "Es menor"
        esMayor = "Es mayor"
        if self.fechaLimite :
            fechaCompleta = str(self.fechaLimite).split(' ')[0]
            fechaCompleta = fechaCompleta.split('-')
            fecha1 = datetime.datetime(int(fechaCompleta[0]), int(fechaCompleta[1]), int(fechaCompleta[2]))
            if fecha1 < fecha2 :
                # self.fechaLimite = datetime.datetime.now()
                raise exceptions.ValidationError("La fecha límite al solicitante no puede ser menor al día de hoy .")
            else:
                _logger.info("||||-:   "+esMayor)
        if self.porCubrirAnticipo:
            fechaCompleta = str(self.porCubrirAnticipo).split(' ')[0]
            fechaCompleta = fechaCompleta.split('-')
            fecha1 = datetime.datetime(int(fechaCompleta[0]), int(fechaCompleta[1]), int(fechaCompleta[2]))
            if fecha1 < fecha2 :
                # self.fechaLimite = datetime.datetime.now()
                raise exceptions.ValidationError("La fecha de compromiso de adelanto en aprobación no puede ser menor al día de hoy .")
        if self.fechaLimiteComprobacionFinanzas:
            fechaCompleta = str(self.fechaLimiteComprobacionFinanzas).split(' ')[0]
            fechaCompleta = fechaCompleta.split('-')
            fecha1 = datetime.datetime(int(fechaCompleta[0]), int(fechaCompleta[1]), int(fechaCompleta[2]))
            if fecha1 < fecha2 :
                # self.fechaLimite = datetime.datetime.now()
                raise exceptions.ValidationError("La fecha limite de comprobacion en aprobaciòn no puede ser menor al día de hoy .")
    # --- MOTIVOS | SON LOS MOTIVOS DEL GASTO (QUIEN SOLICITA - USUARIO FINAL)
    # MODELO : motivos
    #   _name = 'motivos'
    #   _description = 'Motivos de un gasto'
    motivos = fields.One2many('motivos', 'gasto', string = "Motivo",track_visibility='onchange')
    totalMontoMotivosFinal = fields.Float(string = 'Total monto de motivos',track_visibility='onchange')
    def hola(self):
        return { 'warning': { 'title': 'Mensaje de aviso ', 'message': 'La fecha de compromiso de adelanto es mayor a la fecha limite, usted puede continuar'} }
    @api.multi
    @api.onchange('motivos')
    def calcularTotalMotivos(self):
        message = ""
        mess = {}
        listaDeMotivos = self.motivos
        if listaDeMotivos != []:
            montoTotal = 0.0
            for motivo in listaDeMotivos:
                montoTotal += motivo.monto
            if montoTotal > self.montoRequerido :
                raise exceptions.ValidationError("La suma de los montos no puede ser mayor al monto requerido .")
            else :
                self.totalMontoMotivosFinal = montoTotal
            if montoTotal != self.totalMontoMotivosFinal:
                raise exceptions.ValidationError("No puedes modificar el monto total de los motivos.")
    @api.constrains('totalMontoMotivosFinal')
    def verificaTotalMotivos(self):
        listaDeMotivos = self.motivos
        if listaDeMotivos != []:
            montoTotal = 0.0
            for motivo in listaDeMotivos:
                montoTotal += motivo.monto
            if montoTotal != self.totalMontoMotivosFinal:
                raise exceptions.ValidationError("No puedes modificar el monto total de los motivos.")
    # --- PAGO A SOLICITANTE | ESTOS SON LOS PAGOS QUE SE ESTAN DANDO AL SOLICITANTE (LO EDITA EL AREA DE FINANZAS)
    # NOTA : El modelo dice devolución cambiar a pago a solicitante
    # MODELO : devolucion
    #   _name = "gastos.devolucion"
    #   _description = 'Pago a solicitante'
    devoluciones = fields.One2many('gastos.devolucion', 'gasto' , string = 'Pago a solicitante', track_visibility = 'onchange')
    totalPagosSolitantes = fields.Float(string = "Total monto pagado", track_visibility='onchange')
    montoPorCubrir = fields.Float(string = "Monto por cubrir a solicitante", track_visibility='onchange')
    @api.onchange('devoluciones')
    def calcularTotalPagoDevolucion(self):
        listaDevoluciones = self.devoluciones
        montoPagadoTotal = 0.0
        if listaDevoluciones != []:
            for devolucion in listaDevoluciones:
                montoPagadoTotal += devolucion.montoEntregado
        if montoPagadoTotal != self.totalPagosSolitantes :
            self.montoPorCubrir = (self.montoAprobadoFinal-self.montoAnticipado) - montoPagadoTotal
        else :
            self.montoPorCubrir = (self.montoAprobadoFinal-self.montoAnticipado) - self.totalPagosSolitantes
        self.totalPagosSolitantes = montoPagadoTotal
    @api.constrains('totalPagosSolitantes','montoPorCubrir')
    def verificaTotalPagosSolicitantes(self):
        listaDevoluciones = self.devoluciones
        montoPagadoTotal = 0.0
        if listaDevoluciones != []:
            for devolucion in listaDevoluciones:
                montoPagadoTotal += devolucion.montoEntregado
        if montoPagadoTotal != self.totalPagosSolitantes :
            raise exceptions.ValidationError("No puedes modificar el monto total de las devoluciones.")
        if self.montoAprobadoFinal  :
            if self.totalPagosSolitantes :
                montoPorCubrir = (self.montoAprobadoFinal-self.montoAnticipado) - self.totalPagosSolitantes
                if montoPorCubrir != self.montoPorCubrir :
                    raise exceptions.ValidationError("No puedes modificar el monto por cubrir de las devoluciones.")
    # --- COMPROBACIÓNES | PARTE DE LOS CAMPOS LOS UTILIZA EL USUARIO FINAL Y OTROS EL AREA DE FINANZAS
    # _name = 'gastos.comprobaciones'
    # _description = 'Tipos de comprobaciónes del gasto'
    comprobaciones = fields.One2many('gastos.comprobaciones', 'comprobante', string = "Comprobante",track_visibility='onchange')
    montoPagadoComprobado = fields.Float(string = "Monto pagado", track_visibility='onchange')
    montoComprobado = fields.Float(string = "Monto comprobado", track_visibility='onchange')
    montoComprobadoAprobado =  fields.Float(string = " Monto comprobado aprobado", track_visibility='onchange')
    estatusComprobaciones = fields.Selection([('activo','Puede agregar comprobaciónes'), ('desactivado','No puede agregar comprobaciónes')], default='activo',string = "Status de comprobaciónes", track_visibility='onchange')
    montoPorComprobar =  fields.Float(string = "Monto por comprobar", track_visibility='onchange')
    @api.multi
    def activarComprovaciones(self):
        for rec in self : 
            rec.write({'estatusComprobaciones':'activo'})
    @api.multi
    def desactivaComprovaciones(self):
        for rec in self : 
            rec.write({'estatusComprobaciones':'desactivado'})
    @api.onchange('comprobaciones')
    def calcularTotalComprobaciones(self):
        listaComprobaciones = self.comprobaciones
        montoPagadoTotal = 0.0
        montoComprobadoAprobadoTotal = 0.0
        if listaComprobaciones != []:
            for comprobacion in listaComprobaciones:
                montoPagadoTotal += comprobacion.monto
                montoComprobadoAprobadoTotal += comprobacion.montoAprobado
            self.montoComprobado = montoPagadoTotal
            self.montoComprobadoAprobado = montoComprobadoAprobadoTotal
    #Codigo de estatus del gasto
    @api.multi
    def cancelarGasto(self):
        for rec in self : 
            rec.write({'statusGasto':'cancelado'})
            rec.write({'autorizacionLider':'rechazado'})
            rec.write({'autorizacionFinanzas':'rechazado'})
    @api.multi
    def reactivaGasto(self) : 
        for rec in self : 
            rec.write({'statusGasto':'aprovacion'})
            rec.write({'autorizacionFinanzas':'aprobado'})
            rec.write({'autorizacionLider':'aprobado'})
    @api.multi
    def autorizarGasto(self):
        for rec in self : 
            rec.write({'statusGasto':'autorizacion'})
            rec.write({'autorizacionLider':'aprobado'})
            rec.write({'autorizacionFinanzas':'enEspera'})
    #quienSolcita     = fields.Char(string="Quien solicita?" ,track_visibility='onchange')
    #quienesAutorizan = fields.One2many('res.users', 'gastoAutoriza', string = "Responsable de autorizacion",track_visibility='onchange')
    #quienesAutorizan = fields.Char(string = "Responsable de autorizacion", track_visibility='onchange')
    quienesReciben   = fields.One2many('res.users', 'gastoRecibe', string = "Quien (es) reciben",track_visibility='onchange')
    montoAdelantado = fields.Float(string = 'Monto adelanto',track_visibility='onchange')
    formaDepagoAnticipo         = fields.Selection((('Efectivo','Efectivo'), ('Cheque','Cheque'),('Deposito','Deposito'),('Transferencia','Transferencia')), string = "Forma de pago",track_visibility='onchange')
    comoAplicaContablemente     = fields.Selection((('Opcion','Opcion'),('Opcion','Opcion'),('Opcion','Opcion')), string = "Como aplica contablemente",track_visibility='onchange')
    fechaPago                   = fields.Datetime(string = 'Fecha pago de adelanto',track_visibility='onchange')
    fechaLimiteDeComprobacion   = fields.Datetime(string = 'Fecha limite de comprobacion',track_visibility='onchange')
    anticipoCubierto            = fields.Float(string = 'Anticipo cubierto',track_visibility='onchange')
    #quienValida                 = fields.One2many('hr.employee', 'gastoValida', string = "Validado por",track_visibility='onchange')
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
    # --------------------
    #Modelo de devoluciónes
    pagos = fields.One2many('gastos.pago', 'gasto' , string = 'Pago', track_visibility = 'onchange')    
    montoComprobadoPago = fields.Float(string = "Monto comprobado", track_visibility='onchange')
    montoComprobadoAprobadoPago = fields.Float(string = "Monto comprobado aprobado", track_visibility='onchange')
    montoPagadoOriPago = fields.Float(string = "Monto de pago", track_visibility='onchange')
    montoADevolverPago = fields.Float(string = "Monto a devolver", track_visibility='onchange')
    montoDevueltoPago = fields.Float(string = "Monto devuelto", track_visibility='onchange')
    @api.onchange('pagos')
    def calcularTotalMontoADevolver(self):
        listaPagos = self.pagos
        montoPagadoTotal = 0.0
        if listaPagos != []:
            for pago in listaPagos:
                montoPagadoTotal += pago.montoPagado
            self.montoADevolverPago = montoPagadoTotal
            self.montoDevueltoPago = self.montoComprobadoAprobado - self.totalPagosSolitantes
    totalDeMontoPagado = fields.Float(string = 'Total')
    def computarDiasAtrasoPago(self):
        for rec in self:
            fecha = str(rec.create_date).split(' ')[0]
            converted_date = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
            rec.diasAtrasoPago = (datetime.date.today() - converted_date).days
    # ---------------------------------------------------------------------------------
    # facturas = fields.One2many('account.invoice','x_facturasGastos','Facturas')

    #Conceptos para comprobaciónes
    archivoXMLConceptos=fields.Binary(store=True,readonly=False,string="XML con conceptos")
    @api.multi
    @api.onchange('archivoXMLConceptos')
    def llenaConceptos(self):
        if(self.archivoXMLConceptos):
            f2=base64.b64decode(self.archivoXMLConceptos)
            H=StringIO(f2)
            mimetype = guess_mimetype(f2 or b'')
            if(mimetype=='image/svg+xml' or mimetype=='application/octet-stream'):
                tree = minidom.parse(H)
                conceptos=tree.getElementsByTagName("cfdi:Concepto")
                # _logger.info("|llenaConceptos|/|-:   "+str(conceptos))
                vals = []
                for concepto in conceptos:
                    unidad=concepto.getAttribute("unidad")
                    descripcion=concepto.getAttribute("descripcion")
                    valorUnitario=concepto.getAttribute("valorUnitario")
                    vals.append((0, 0, {
                        'concepto': str(unidad), 
                        'descripcion': str(descripcion),
                        'monto': str(valorUnitario),
                        'archivoXML' : self.archivoXMLConceptos,
                        'tipoDeComprobante': 'XML'
                    }))
                self.update({'comprobaciones': vals})
    # Conceptos para devoluciónes
    archivoXMLDevoluciones =fields.Binary(store=True,readonly=False,string="XML con conceptos")
    @api.multi
    @api.onchange('archivoXMLDevoluciones')
    def llenaConceptosDev(self):
        if(self.archivoXMLDevoluciones):
            f2=base64.b64decode(self.archivoXMLDevoluciones)
            H=StringIO(f2)
            mimetype = guess_mimetype(f2 or b'')
            if(mimetype=='image/svg+xml' or mimetype=='application/octet-stream'):
                tree = minidom.parse(H)
                conceptos=tree.getElementsByTagName("cfdi:Concepto")
                # _logger.info("|llenaConceptos|/|-:   "+str(conceptos))
                vals = []
                for concepto in conceptos:
                    unidad=concepto.getAttribute("unidad")
                    descripcion=concepto.getAttribute("descripcion")
                    valorUnitario=concepto.getAttribute("valorUnitario")
                    vals.append((0, 0, {
                        'concepto': str(unidad), 
                        'descripcion': str(descripcion),
                        'montoPagado': str(valorUnitario),
                        'archivoXML' : self.archivoXMLDevoluciones
                    }))
                self.update({'pagos': vals})
class usuarios_gastos(models.Model):
    _inherit = 'res.users'
    gastoSolicitante = fields.One2many('gastos', 'quienSolcita', string="Gasto solicitante")
    gastoAtoriza = fields.One2many('gastos', 'quienesAutorizan', string="Gasto autorizo")
    gastoAutoriza = fields.Many2one('gastos', string="Gasto autoriza")
    gastoAprobacion = fields.One2many('gastos', 'quienValida', string="Gasto aprobación")
    gastoRecibe = fields.Many2one('gastos', string="Gasto autoriza")
    devoResponsableAjuste = fields.Text(string = "Devolucion responsable",track_visibility='onchange')
    pagoSolicitanteAutoriza = fields.One2many('gastos.devolucion','quienesReciben' ,string="Pago autoriza")
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
    tiket = fields.Many2one('helpdesk.ticket', string = "Número de tiket",track_visibility='onchange',copied=True)
    estadoTiket = fields.Text(string = "Estado tiket",track_visibility='onchange' )
    @api.onchange('tiket')
    def getEstadoTiket(self):
        if self.tiket :
            _logger.info("||||-:   "+str(self.tiket.stage_id.name))
            self.estadoTiket = self.tiket.stage_id.name
    motivoDescripcion = fields.Text(string = "Descripción de gasto",track_visibility='onchange')
    motivoNumeroTicket = fields.Text(string = "Número de ticket",track_visibility='onchange')
    motivoConcepto = fields.Text(string = "Motivo (Concepto)",track_visibility='onchange')
    motivoCentroCostos = fields.Many2one('res.partner', string = "Centro de costos (Cliente)",track_visibility='onchange')
    motivoTipoDeMotivo = fields.Selection((('!','1'), ('2','2')), string = "Tipo de motivo",track_visibility='onchange')
    monto = fields.Float(string = "Monto", track_visibility='onchange')
    @api.constrains('monto')
    def verificaMonto(self):
        if self.monto == 0.0:
            raise exceptions.ValidationError("En MOTIVOS : El monto no puede ser igual a cero.")
class comprobaciones(models.Model):
    _name = 'gastos.comprobaciones'
    _description = 'Tipos de comprobaciónes del gasto'
    comprobante             = fields.Many2one('gastos', string = "Comprobación ", track_visibility='onchange')
    #USUARIO
        # Concepto
        # Descripción
        # Justificación
        # Tipo de Comprobante
        # Evidencia
        # Monto aprobado
    #FINANSAS
        # Porcentaje aceptado
        # Justicación contable de Porcentaje no aceptado (Con comprobante fiscal)
        # Aplicación contable
    # -------Usuario------------
    concepto                = fields.Text(string = "Concepto",      track_visibility='onchange')
    descripcion             = fields.Text(string = "Descripción",   track_visibility='onchange')
    justificacon            = fields.Text(string = "Justificación", track_visibility='onchange')
    tipoDeComprobante       = fields.Selection((('Factura','Factura'),('FacturaSinIva','Factura sin IVA'),('TiketFacturable','Ticket facturable'),('Tiket','Ticket'),('Nota','Nota'),('XML','XML')), string = "Tipo de Comprobante",track_visibility='onchange')
    comprobantes            = fields.Many2many('ir.attachment', string="Evidencia")

    archivoXML              = fields.Binary(store=True,readonly=False,string="Evidencia")
    # -------Finanzas------------
    porcentajeAceptado      = fields.Float(string = "Porcentaje Aceptado",track_visibility='onchange')
    montoAprobado           = fields.Float(string = "Monto aprobado",track_visibility='onchange')
    cuentaContableDestino   = fields.Text(string = "Aplicación contable", track_visibility='onchange')
    montoAprobadooriginalMante = fields.Float(string = "Monto aprobado originalmente", track_visibility='onchange')
    justificacionContable   = fields.Text(string = "Justificación contable", track_visibility='onchange')
    #----------------------------
    monto                   = fields.Float(string = "Monto",         track_visibility='onchange')
    nombre                  = fields.Char(string="Nombre de comprobación", track_visibility='onchange')
    # montoJustificado        = fields.Float(string = 'Monto aprobado', compute='calcularMontoAprobado', track_visibility='onchange')
    centoDeCostos           = fields.Text(string = "Centro de Costos", track_visibility='onchange')
    cliente = fields.Many2one('res.partner', string = 'Cliente', track_visibility='onchange')
    servicio = fields.Text(string = 'Servicio')
    @api.onchange('porcentajeAceptado')
    def calcularMontoAprobado(self):
        if self.porcentajeAceptado : 
            if self.monto :
                self.montoAprobado = self.monto * self.porcentajeAceptado
    @api.multi
    @api.onchange('archivoXML')
    def llenaCampos(self):
        if(self.archivoXML):
            f2=base64.b64decode(self.archivoXML)
            H=StringIO(f2)
            mimetype = guess_mimetype(f2 or b'')
            if(mimetype=='image/svg+xml' or mimetype=='application/octet-stream'):
                tree = minidom.parse(H)
                unidad = tree.getElementsByTagName("cfdi:Concepto")[0].getAttribute("unidad")
                descripcion = tree.getElementsByTagName("cfdi:Concepto")[0].getAttribute("descripcion")
                valorUnitario = tree.getElementsByTagName("cfdi:Concepto")[0].getAttribute("valorUnitario")
                #Write in campos
                self.concepto       = str(unidad)
                self.descripcion    = str(descripcion)
                self.monto          = str(valorUnitario)
                self.tipoDeComprobante = 'XML'            
class PagoSolicitante(models.Model):
    _name = 'gastos.devolucion'
    _description = 'Pago a solicitante'
    gasto = fields.Many2one('gastos', string="Pagos solitatados", track_visibility='onchange')
    quienesReciben = fields.Many2one('res.users',string = "Quien recibe", track_visibility='onchange', default=lambda self: self.env.user)
    #datos tabla compleneto/Devolucion
    montoEntregado = fields.Float(string = "Monto")
    fecha = fields.Datetime(string = 'Fecha', track_visibility = 'onchange')
    formaDePago = fields.Selection([('Efectivo','Efectivo'), ('Cheque','Cheque'),('Deposito','Deposito'),('Transferencia','Transferencia'),('pagoSoloEx','Pago en una sola exhibición')], string = "Forma de pago")
    fechaLimite = fields.Datetime(string = 'Fecha límite comprobación', track_visibility = 'onchange')
    evidencia = fields.Many2many('ir.attachment', string="Evidencia")
    archivo=fields.Binary(store=True,readonly=False,string="Evidencia")
    montoAprobadoOriginalMante  = fields.Float(string = "Monto aprobado originalmente", track_visibility='onchange')
    montoPagado = fields.Float(string = "Monto pagado")
    #Campos agregados
    banco = fields.Selection((('bajio','BAJIO'), ('banamex','BANAMEX'),('banorte','BANORTE'),('santnder','SANTANDER'),('hsbc','HSBC'),('azteca','AZTECA'),('bancomer','BANCOMER')), string = "Banco a depositar")
    claveInterbancaria = fields.Char(string="Clave interbancaria", track_visibility='onchange')
    # depositoDeducible = fields.Selection((('si','Si'), ('no','No')), string = "Depósito deducible")
    montodeDucibleI = fields.Float(string = "Monto deducible", track_visibility='onchange')
    montodeNoDucibleI = fields.Float(string = "Monto no deducible", track_visibility='onchange')
    @api.constrains('montoEntregado')
    def verificaMonto(self):
        if self.montoEntregado == 0.0:
            raise exceptions.ValidationError("En PAGOS A SOLICITANTE : El monto no puede ser igual a cero.")
    fechaTransf = fields.Datetime(string = 'Fecha de transferencia', track_visibility = 'onchange', readonly=False )
    fechaTransfDeducible = fields.Datetime(string = 'Fecha de transferencia deducible', track_visibility = 'onchange', readonly=False )
    @api.onchange('montodeDucibleI','montodeNoDucibleI')
    def sumaMontosDeducibles(self):
        self.montoEntregado = self.montodeDucibleI + self.montodeNoDucibleI
    @api.onchange('fecha')
    def computarDiasAtrasoPago(self):
        if self.fecha :
            fechaCompleta = str(self.fecha).split(' ')[0]
            fechaCompleta = fechaCompleta.split('-')
            fecha1 = datetime.datetime(int(fechaCompleta[0]), int(fechaCompleta[1]), int(fechaCompleta[2]))
            fechaHoy = datetime.date.today()
            fechaHoy = str(fechaHoy)
            fechaHoy = fechaHoy.split('-')
            fecha2 = datetime.datetime(int(fechaHoy[0]), int(fechaHoy[1]), int(fechaHoy[2]))
            message = ""
            mess = {}
            esMenor = "Es menor"
            esMayor = "Es mayor"
            if fecha1 <= fecha2 :
                _logger.info("||||-:   "+esMenor)
            else:
                self.fecha = ""
                message = ("El pago no puede ser mayor al día de hoy .")
                mess = { 'title': _('Error'), 'message' : message}
                return {'warning': mess}
    @api.multi
    @api.onchange('archivo')
    def llenaCampos(self):
        if(self.archivo):
            f2=base64.b64decode(self.archivo)
            H=StringIO(f2)
            mimetype = guess_mimetype(f2 or b'')
            if(mimetype=='image/svg+xml' or mimetype=='application/octet-stream'):
                tree = minidom.parse(H)
                # total=tree.getElementsByTagName("cfdi:Comprobante")[0].getAttribute("Total")
                total=tree.getElementsByTagName("cfdi:Comprobante")[0].getAttribute("total")
                totalImpuestosTrasladados=tree.getElementsByTagName("cfdi:Impuestos")[0].getAttribute("totalImpuestosTrasladados")
                totalConImpuestos = float(totalImpuestosTrasladados) + float(total)
                formaDePago1=tree.getElementsByTagName("cfdi:Comprobante")[0].getAttribute("formaDePago")
                #Write in campos
                if (str(formaDePago1) == 'Pago en una sola exhibición'):
                    self.formaDePago = 'pagoSoloEx'
                self.montodeDucibleI = float(totalConImpuestos)
class Pagos(models.Model):
    _name = 'gastos.pago'
    _description = 'Pagos de los gastos'
    gasto = fields.Many2one('gastos', string="Pago relacionado", track_visibility='onchange')
    # -------Usuario------------
    concepto = fields.Text(string = "Concepto", track_visibility='onchange')
    fechaDePago = fields.Datetime(string = 'Fecha de pago', track_visibility='onchange')
    montoPagado = fields.Float(string = "Monto", track_visibility='onchange')
    formaDePago = fields.Selection((('Efectivo','Efectivo'), ('Cheque','Cheque'),('Deposito','Deposito'),('Transferencia','Transferencia'),('Nómina','Nómina')), string = "Forma de pago")
    comprobanteDePago = fields.Many2many('ir.attachment', string="Evidencia")

    descripcion             = fields.Text(string = "Descripción",   track_visibility='onchange')
    archivoXML              = fields.Binary(store=True,readonly=False,string="Evidencia")
    # -----------------------
    #datos tabla pago de complemento/devolucion
    montoSolicitante = fields.Float(string = "Solicitante")
    montoEmpresa = fields.Float(string = "Empresa")
    fechaProgramada = fields.Datetime(string = 'Fecha programada')
    totalMonto = fields.Float(string = "Total de monto")


    @api.multi
    @api.onchange('archivoXML')
    def llenaCampos(self):
        if(self.archivoXML):
            f2=base64.b64decode(self.archivoXML)
            H=StringIO(f2)
            mimetype = guess_mimetype(f2 or b'')
            if(mimetype=='image/svg+xml' or mimetype=='application/octet-stream'):
                tree = minidom.parse(H)
                unidad = tree.getElementsByTagName("cfdi:Concepto")[0].getAttribute("unidad")
                descripcion = tree.getElementsByTagName("cfdi:Concepto")[0].getAttribute("descripcion")
                valorUnitario = tree.getElementsByTagName("cfdi:Concepto")[0].getAttribute("valorUnitario")
                #Write in campos
                self.concepto       = str(unidad)
                self.descripcion    = str(descripcion)
                self.montoPagado    = str(valorUnitario)