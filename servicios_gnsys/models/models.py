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
    _inherit = 'mail.thread'
    _description = 'Servicios GNSYS'
    

    productos = fields.One2many('product.product', 'servicio', string="Productos")
    
    descripcion = fields.Text(string="Descripción")
    rentaMensual = fields.Text(string="Renta mensual")
    tipo = fields.Selection([('1','Costo por página procesada BN o color'),('2','Renta base con páginas incluidas BN o color + pag. excedentes'),('3','Renta base + costo de página procesada BN o color'),('4','Renta base con páginas incluidas BN + clic de color + excedentes BN'),('5','Renta global + costo de página procesada BN o color'),('6','SERVICIO DE PCOUNTER'),('7','RENTA MENSUAL DE LICENCIA EMBEDED')],string="Tipo de cobro")
    bolsaBN = fields.Integer(string="Bolsa B/N")
    clickExcedenteBN = fields.Float(string="Click excedente B/N")
    procesadoBN = fields.Integer(string="Procesado B/N")

    bolsaColor = fields.Integer(string="Bolsa color")
    clickExcedenteColor = fields.Float(string="Click excedente color")
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
    
    name = fields.Char(string="Nombre")
    servicio = fields.One2many('servicios', 'contrato', string="Servicio")
    
    cliente = fields.Many2one('res.partner', string='Cliente')
    idtmpp = fields.Char(string="idTMPp")
    tipoDeCliente = fields.Selection([('A','A'),('B','B'),('C','C'),('VIP','VIP'),('OTRO','Otro')], default='A', string="Tipo de cliente")
    mesaDeAyudaPropia = fields.Boolean(string="Mesa de ayuda propia", default=False)
    
    ejecutivoDeCuenta = fields.Many2one('hr.employee', string='Ejecutivo de cuenta')
    vendedor = fields.Many2one('hr.employee', string="Vendedor")
    
    tipoDeContrato = fields.Selection([('ARRENDAMIENTO','Arrendamiento'),('DEMOSTRACION','Demostración'),('OTRO','Otro')], default='ARRENDAMIENTO', string="Tipo de contrato")
    vigenciaDelContrato = fields.Selection([('INDEFINIDO','Indefinido'),('12','12'),('18','18'),('24','24'),('36','36'),('OTRO','Otro')], default='12', string="Vigencia del contrato (meses)")
    fechaDeInicioDeContrato = fields.Datetime(string = 'Fecha de inicio de contrato',track_visibility='onchange')
    fechaDeFinDeContrato = fields.Datetime(string = 'Fecha de finalización de contrato',track_visibility='onchange')
    ordenDeCompra = fields.Boolean(string="Orden de compra", default=False)
    
    tonerGenerico = fields.Boolean(string="Tóner genérico", default=False)
    equiposNuevos = fields.Boolean(string="Equipos nuevos", default=False)
    periodicidad = fields.Selection([('BIMESTRAL','Bimestral'),('TRIMESTRAL','Trimestral'),('CUATRIMESTRAL','Cuatrimestral'),('SEMESTRAL','Semestral')], default='BIMESTRAL', string="Periodicidad")
    idTechraRef = fields.Integer(string="ID techra ref")
    conteo = fields.Integer(string="Conteo")

    adjuntos = fields.Selection([('CONTRATO DEBIDAMENTE REQUISITADO Y FIRMADO','Contrato debidamente requisitado y firmado'),('CARTA DE INTENCION','Carta de intención')], default='CONTRATO DEBIDAMENTE REQUISITADO Y FIRMADO', string="Se adjunta")
    documentacion = fields.Many2many('ir.attachment', string="Documentación")

    #----------------------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------------------
    formaDePago = fields.Selection([('3','01 - Efectivo') ,('2','02 - Cheque nominativo') ,('1','03 - Transferencia electrónica de fondos') ,('4','04 - Tarjeta de crédito') ,('7','05 - Monedero electrónico') ,('10','06 - Dinero electrónico') ,('11','08 - Vales de despensa') ,('12','12 - Dación en pago') ,('13','13 - Pago por subrogación') ,('14','14 - Pago por consignación') ,('15','15 - Condonación') ,('16','17 - Compensación') ,('17','23 - Novación') ,('18','24 - Confusión') ,('19','25 - Remisión de deuda') ,('20','26 - Prescripción o caducidad') ,('21','27 - A satisfacción del acreedor') ,('5','28 - Tarjeta de debito') ,('6','29 - Tarjeta de servicios') ,('9','30 - Aplicación de anticipos') ,('22','30 - Aplicación de anticipos') ,('8','99 - Por definir')], string = "Forma de pago",track_visibility='onchange')

    cuentaBancaria  = fields.Selection([('24','BAJIO - 9777600201 - MON NAC') ,('19','BANAMEX - 002180418300272792 - MONEDA NAC') ,('12','BANAMEX - 002180700725697152 - CHEQUES M.') ,('16','CI BANCO - 0001120336 - MONEDA NAC') ,('17','MULTIVA - 0004738918 - MONEDA NAC')], string = "Cuenta bancaria definida",track_visibility='onchange')
class cliente_contratos(models.Model):
    _inherit = 'res.partner'
    contrato = fields.One2many('contrato', 'cliente', string="Contratos")
    

class ejecutivo_de_cuenta_contratos(models.Model):
    _inherit = 'hr.employee'
    contratoEjecutivoDeCuenta = fields.One2many('contrato', 'ejecutivoDeCuenta', string="Contratos asociados al ejecutivo de cuenta")
    contratoVendedor = fields.One2many('contrato', 'vendedor', string="Contratos asociados al vendedor")
