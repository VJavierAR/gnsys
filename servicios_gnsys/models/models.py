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
    fechaDeInicioDeServicio = fields.Datetime(string = 'Fecha de inicio de servicio',track_visibility='onchange')
    fechaDeFinDeServicio = fields.Datetime(string = 'Fecha de finalización de servicio',track_visibility='onchange')
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
    
    
    fecha = fields.Datetime(string = 'Anexo',track_visibility='onchange')
    diaCorte = fields.Integer(string="Día de corte",track_visibility='onchange')
    renta = fields.Selection([('0','82121503 Impresión digital') ,('1','82121500 Impresión') ,('2','43212105 Impresoras láser') ,('3','44103105 Cartuchos de tinta') ,('4','80161801 Servicio de alquiler o leasing de fotocopiadoras') ,('5','81101707 Mantenimiento de equipos de impresión') ,('6','82121701 Servicios de copias en blanco y negro o de cotejo') ,('7','82121702 Servicios de copias a color o de cotejo') ,('8','44103103 Tóner para impresoras o fax') ,('9','44101700 Accesorios para impresoras, fotocopiadoras y aparatos de fax') ,('10','81161800 Servicios de alquiler o arrendamiento de equipos o plataformas de voz y datos o multimedia') ,('11','44101503 Máquinas multifuncionales') ,('12','80111616 Personal temporal de servicio al cliente') ,('13','93151507 Procedimientos o servicios administrativos') ,('14','84111506 Servicios de facturación') ,('15','81112005 Servicio de escaneo de documentos') ,('16','44103125 Kit de mantenimiento de impresoras') ,('17','81111811 Servicios de soporte técnico o de mesa de ayuda') ,('18','81112306 Mantenimiento de impresoras') ,('19','43233410 Software de controladores de impresoras') ,('20','80161800 Servicios de alquiler o arrendamiento de equipo de oficina') ,('21','25101503 Carros') ,('22','82121700 Fotocopiado')], string = "Renta",track_visibility='onchange')
    impresiones = fields.Selection([('0','82121503 Impresión digital') ,('1','82121500 Impresión') ,('2','43212105 Impresoras láser') ,('3','44103105 Cartuchos de tinta') ,('4','80161801 Servicio de alquiler o leasing de fotocopiadoras') ,('5','81101707 Mantenimiento de equipos de impresión') ,('6','82121701 Servicios de copias en blanco y negro o de cotejo') ,('7','82121702 Servicios de copias a color o de cotejo') ,('8','44103103 Tóner para impresoras o fax') ,('9','44101700 Accesorios para impresoras, fotocopiadoras y aparatos de fax') ,('10','81161800 Servicios de alquiler o arrendamiento de equipos o plataformas de voz y datos o multimedia') ,('11','44101503 Máquinas multifuncionales') ,('12','80111616 Personal temporal de servicio al cliente') ,('13','93151507 Procedimientos o servicios administrativos') ,('14','84111506 Servicios de facturación') ,('15','81112005 Servicio de escaneo de documentos') ,('16','44103125 Kit de mantenimiento de impresoras') ,('17','81111811 Servicios de soporte técnico o de mesa de ayuda') ,('18','81112306 Mantenimiento de impresoras') ,('19','43233410 Software de controladores de impresoras') ,('20','80161800 Servicios de alquiler o arrendamiento de equipo de oficina') ,('21','25101503 Carros') ,('22','82121700 Fotocopiado')], string = "Impresiones",track_visibility='onchange')

    @api.multi
    def crear_solicitud_arrendamineto(self):
        for record in self:            
            if len(record.x_studio_field_7jBI3) > 0:
                if self.x_studio_solicitud.id != False and self.x_studio_solicitud.state != 'sale':
                    sale = self.x_studio_solicitud
                    self.env.cr.execute("delete from sale_order_line where order_id = " + str(sale.id) +";")
                    for c in self.x_studio_field_7jBI3:
                        datosr={'order_id' : sale.id, 'product_id' : c.id, 'product_uom_qty' : c.x_studio_cantidad_pedida}                                                
                        self.env['sale.order.line'].create(datosr)
                        self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Arrendamiento' where  id = " + str(sale.id) + ";")                        
                else:                
                    sale = self.env['sale.order'].create({'partner_id' : record.contrato.cliente.id
                                                                 ,'origin' : "Servicio: " + str(record.id)
                                                                 , 'x_studio_tipo_de_solicitud' : 'Arrendamiento'
                                                                 , 'x_studio_requiere_instalacin' : True                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
                                                                 , 'warehouse_id' : 5865   ##Id GENESIS AGRICOLA REFACCIONES  stock.warehouse
                                                                 , 'team_id' : 1                                                                  
                                                                })
                    record['x_studio_solicitud'] = sale.id
                    for c in record.x_studio_field_7jBI3:
                        datosr={'order_id' : sale.id, 'product_id' : c.id, 'product_uom_qty' : c.x_studio_cantidad_pedida,'price_unit': 0}                        
                        self.env['sale.order.line'].create(datosr)
                        sale.env['sale.order'].write({'x_studio_tipo_de_solicitud' : 'Venta'})                        
                        self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Arrendamiento' where  id = " + str(sale.id) + ";")        
    
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
    ordenDeCompra = fields.Text(string="Orden de compra",track_visibility='onchange')
    instruccionesOrdenDeCompra = fields.Text(string="Instrucciones de orden de compra",track_visibility='onchange')
    
    tonerGenerico = fields.Boolean(string="Tóner genérico", default=False)
    equiposNuevos = fields.Boolean(string="Equipos nuevos", default=False)
    periodicidad = fields.Selection([('MENSUAL','Mensual'),('BIMESTRAL','Bimestral'),('TRIMESTRAL','Trimestral'),('CUATRIMESTRAL','Cuatrimestral'),('SEMESTRAL','Semestral'),('ANUAL','Anual'),('CONTRATO','Contrato')], default='BIMESTRAL', string="Periodicidad")
    idTechraRef = fields.Integer(string="ID techra ref")

    adjuntos = fields.Selection([('CONTRATO DEBIDAMENTE REQUISITADO Y FIRMADO','Contrato debidamente requisitado y firmado'),('CARTA DE INTENCION','Carta de intención')], default='CONTRATO DEBIDAMENTE REQUISITADO Y FIRMADO', string="Se adjunta")
    documentacion = fields.Many2many('ir.attachment', string="Documentación")

    #------------------------------------------------------------------------------------------
    #Contrato

    formaDePago = fields.Selection([('3','01 - Efectivo') ,('2','02 - Cheque nominativo') ,('1','03 - Transferencia electrónica de fondos') ,('4','04 - Tarjeta de crédito') ,('7','05 - Monedero electrónico') ,('10','06 - Dinero electrónico') ,('11','08 - Vales de despensa') ,('12','12 - Dación en pago') ,('13','13 - Pago por subrogación') ,('14','14 - Pago por consignación') ,('15','15 - Condonación') ,('16','17 - Compensación') ,('17','23 - Novación') ,('18','24 - Confusión') ,('19','25 - Remisión de deuda') ,('20','26 - Prescripción o caducidad') ,('21','27 - A satisfacción del acreedor') ,('5','28 - Tarjeta de debito') ,('6','29 - Tarjeta de servicios') ,('9','30 - Aplicación de anticipos') ,('22','30 - Aplicación de anticipos') ,('8','99 - Por definir')], string = "Forma de pago",track_visibility='onchange')

    banco = fields.Selection([(1, ' - BNM840515VB1'), (2, ' - 12799.44'), (3, ' - SIN9412025I4'), (4, 'BAJIO - BBA940707IE1'), (5, 'BANAM - BNM840515VB1'), (6, 'BANAMEX - BNM840515VB1'), (7, 'BANAMEX - '), (8, 'BANAMEX - BNM840515VB'), (9, 'BANBAJIO - BBA940707IE1'), (10, 'BANCA MIFEL - BMI9312038R3'), (11, 'BANCO AZTECA - BAI0205236Y8'), (12, 'BANCO BASE - BBS110906HD3'), (13, 'BANCO DEL BAJ�O - BBA940707IE1'), (14, 'BANCO DEL BAJIO SA - BBA940707IE1'), (15, 'BANCO J.P. MORGAN S.A. - BJP-950104-LJ'), (16, 'BANCO J.P. MORGAN S.A. - BJP950104LJ5'), (17, 'BANCO J.P.MORGAN SA - BJP950104LJ5'), (18, 'Banco Mercantil del Norte - BMN930209927'), (19, 'BANCO MERCANTIL DEL NORTE - BMN930209927'), (20, 'BANCO MERCANTIL DEL NORTE S.A. - BMN930209-927'), (21, 'BANCO MERCANTIL DEL NORTE S.A. - BMN930209927'), (22, 'BANCO MULTIVA, SA - BMI061005NY5'), (23, 'BANCO REGIONAL DE MONTERREY S.A. - BRM940216EQ6'), (24, 'BANCO SANTANDER - BSM970519DU8'), (25, 'BANCO SANTANDER (MEXICO) S.A., INSTITUCION DE BANC - BSM970519DU8'), (26, 'BANCO SANTANDER (MEXICO) SA - BSM970519DU8'), (27, 'BANCO VE POR MAS - BVM951002LX0'), (28, 'BANCOMER - BBA830831LJ2'), (29, 'BANCOMER - '), (30, 'BANCONER - BBA830831LJ2'), (31, 'BANK OF AMERICA MEXICO - '), (32, 'BANK OF AMERICA MEXICO - BAM9504035J2'), (33, 'BANORTE - EOP510101UA4'), (34, 'BANORTE - BMN930209927'), (35, 'BANORTE - '), (36, 'BANORTE - BMN930299277'), (37, 'BANORTE - BMN930209 927'), (38, 'BANREGIO - BRM940216EQ6'), (39, 'BBVA BANCOMER - BBA830831LJ2'), (40, 'BBVA Bancomer - BBA830831LJ2'), (41, 'BBVA BANCOMER - '), (42, 'BBVA Bancomer, S.A. - BBA830831LJ2'), (43, 'CI BANCO - BCI001030ECA'), (44, 'CI BANCO - CIB850918BN'), (45, 'CI BANCO - BNY080206UR9'), (46, 'CITI BANAMEX - BNM840515VB1'), (47, 'HSBC - HMI950125KG8'), (48, 'HSBC - '), (49, 'HSBC - HSBC046722'), (50, 'HSBC . - HMI950125KG8'), (51, 'HSBC MEXICO S.A. - HMI-950125KG8'), (52, 'HSBC MEXICO S.A. - HMI950125KG8'), (53, 'HSBC MEXICO S.A. - ASC960408K10'), (54, 'HSBC MEXICO S.A. - '), (55, 'INBURSA - BII931004P61'), (56, 'INBURSA - FCS890710CW5'), (57, 'INVERLAT - SIN9412025I4'), (58, 'J P MORGAN - BJP950104LJ5'), (59, 'J P MORGAN - XEXX010101000'), (60, 'MONEX - BMI9704113PA'), (61, 'MULTIVA - BMI061005NY5'), (62, 'MULTIVA - BMI061005NYS'), (63, 'SANTANDER - BSM970519DU8'), (64, 'SANTANDER - XEXX010101000'), (65, 'SANTANDER - SIN9412025I4'), (66, 'SANTANDER - BSM970519DUB'), (67, 'SANTANDER - '), (68, 'SANTANDER - BMN930299277'), (69, 'SCOTIABANK - SIN9412025I4'), (70, 'SCOTIABANK INVERLAT SA - SIN9412025I4'), (71, 'Scotiabank Inverlat, S.A. - SIN9412025I4'), (72, 'SCOTIANBANK INVERLAT - SIN9412025I4')], string = "Banco",track_visibility='onchange')

    cuentaBancaria  = fields.Selection([('24','BAJIO - 9777600201 - MON NAC') ,('19','BANAMEX - 002180418300272792 - MONEDA NAC') ,('12','BANAMEX - 002180700725697152 - CHEQUES M.') ,('16','CI BANCO - 0001120336 - MONEDA NAC') ,('17','MULTIVA - 0004738918 - MONEDA NAC')], string = "Cuenta bancaria definida",track_visibility='onchange')
    
    metodPago = fields.Selection([('6','PPD Pago en parcialidades o diferido') ,('5','PUE Pago en una sola exhibición')], string = "Método de pago",track_visibility='onchange')
    numCuenta = fields.Integer(string="Número Cuenta",track_visibility='onchange')

    razonSocial  = fields.Char(string = "Razón Social interna",track_visibility='onchange', default=lambda self: self.env.user.razonSocial)

    usoCFDI = fields.Selection([('12','D01 Honorarios médicos, dentales y gastos hospitalarios.') ,('13','D02 Gastos médicos por incapacidad o discapacidad') ,('14','D03 Gastos funerales.') ,('15','D04 Donativos.') ,('16','D05 Intereses reales efectivamente pagados por créditos hipotecarios (casa habitación).') ,('17','D06 Aportaciones voluntarias al SAR.') ,('18','D07 Primas por seguros de gastos médicos.') ,('19','D08 Gastos de transportación escolar obligatoria.') ,('20','D09 Depósitos en cuentas para el ahorro, primas que tengan como base planes de pensiones.') ,('21','D10 Pagos por servicios educativos (colegiaturas)') ,('1','G01 Adquisición de mercancias') ,('2','G02 Devoluciones, descuentos o bonificaciones') ,('3','G03 Gastos en general') ,('4','I01 Construcciones') ,('5','I02 Mobilario y equipo de oficina por inversiones') ,('6','I03 Equipo de transporte') ,('7','I04 Equipo de computo y accesorios') ,('8','I05 Dados, troqueles, moldes, matrices y herramental') ,('9','I06 Comunicaciones telefónicas') ,('10','I07 Comunicaciones satelitales') ,('11','I08 Otra maquinaria y equipo') ,('22','P01 Por definir')], string = "Uso CFDI",track_visibility='onchange')

    diasCredito = fields.Integer(string="Días de crédito",track_visibility='onchange')
    limbo  = fields.Boolean(string="Limbo", default=False)
    activo = fields.Boolean(string="Activo", default=False)
    #Dirección Fiscal
    
    direccion     = fields.Text(string="Dirección",track_visibility='onchange')

    estado       = fields.Selection([('Aguascalientes','Aguascalientes') ,('Baja California','Baja California') ,('Baja California Sur','Baja California Sur') ,('Campeche','Campeche') ,('Ciudad de México" ','Ciudad de México') ,('Coahuila','Coahuila') ,('Colima','Colima') ,('Chiapas','Chiapas') ,('Chihuahua','Chihuahua') ,('Durango','Durango') ,('Estado de México','Estado de México') ,('Guanajuato','Guanajuato') ,('Guerrero','Guerrero') ,('Hidalgo','Hidalgo') ,('Jalisco','Jalisco') ,('Michoacán','Michoacán') ,('Morelos','Morelos') ,('Nayarit','Nayarit') ,('Nuevo León','Nuevo León') ,('Oaxaca','Oaxaca') ,('Puebla','Puebla') ,('Querétaro','Querétaro') ,('Quintana Roo','Quintana Roo') ,('San Luis Potosí','San Luis Potosí') ,('Sinaloa','Sinaloa') ,('Sonora','Sonora') ,('Tabasco','Tabasco') ,('Tamaulipas','Tamaulipas') ,('Tlaxcala','Tlaxcala') ,('Veracruz','Veracruz') ,('Yucatán','Yucatán') ,('Zacatecas','Zacatecas')], string = "Estado",track_visibility='onchange')
    codPostal    = fields.Integer(string="C.P.",track_visibility='onchange')

    #Valores para impresión de factura
    valoresImpresion   = fields.One2many('servicios.valores', 'servicio', string = "Valores para impresión de factura",track_visibility='onchange')
    #razonPrueba  = fields.Many2one('contactos', string="Contactos")
    @api.onchange('cliente')
    def cambiarRazonSocial(self):
        valores = [('0', 'DOCUMENTO INTEGRAL CORPORATIVO, SA DE CV'), ('1', 'GN SYS CORPORATIVO S.A. DE C.V.'),
               ('2', 'GRUPO GNSYS SOLUCIONES SA DE CV'), ('3', 'SERVICIOS CORPORATIVOS GENESIS, S.A DE C.V.')]
        #serviciosTodos = fields.Many2one('res.partner', string='Cliente')
        # serviciosTodos = self.env['contactos']
        
        # id_needed = wt.search([('field1', '=', 'value')]).id
        # new = wt.browse(id_needed)
        # list = [new.field1, new.field2, new.field3]
        if self.cliente :
            self.razonPrueba = self.cliente.razonSocial
            #razonPrueba = self.cliente.razonSocial
            #_logger.info("Estamos aquí  "+str(self.razonPrueba))
            busca = str(self.cliente.razonSocial)
            for valor in valores:
                llave,valor  = valor
                if(busca == llave):
                    self.razonSocial = valor
            self.direccion = self.cliente.contact_address
            self.ejecutivoDeCuenta = self.cliente.x_studio_ejecutivo
            self.vendedor = self.cliente.x_studio_vendedor
    


class cliente_contratos(models.Model):
    _inherit = 'res.partner'
    contrato = fields.One2many('contrato', 'cliente', string="Contratos")
    

class ejecutivo_de_cuenta_contratos(models.Model):
    _inherit = 'hr.employee'
    contratoEjecutivoDeCuenta = fields.One2many('contrato', 'ejecutivoDeCuenta', string="Contratos asociados al ejecutivo de cuenta")
    contratoVendedor = fields.One2many('contrato', 'vendedor', string="Contratos asociados al vendedor")


#Valores para impresión de factura
class Valores_Impresion(models.Model):
    _name = 'servicios.valores'
    _description = 'Valores para impresión de factura'
    servicio = fields.Many2one('servicios', string = "Servicio", track_visibility='onchange')

    #En la vista de techra así estan clasificados los campos 
    campo       = fields.Char()
    valor       = fields.Char()
    selection   = fields.Boolean(default=False)



