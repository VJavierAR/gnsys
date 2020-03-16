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

    #------------------------------------------------------------------------------------------
    #Contrato

    formaDePago = fields.Selection([('3','01 - Efectivo') ,('2','02 - Cheque nominativo') ,('1','03 - Transferencia electrónica de fondos') ,('4','04 - Tarjeta de crédito') ,('7','05 - Monedero electrónico') ,('10','06 - Dinero electrónico') ,('11','08 - Vales de despensa') ,('12','12 - Dación en pago') ,('13','13 - Pago por subrogación') ,('14','14 - Pago por consignación') ,('15','15 - Condonación') ,('16','17 - Compensación') ,('17','23 - Novación') ,('18','24 - Confusión') ,('19','25 - Remisión de deuda') ,('20','26 - Prescripción o caducidad') ,('21','27 - A satisfacción del acreedor') ,('5','28 - Tarjeta de debito') ,('6','29 - Tarjeta de servicios') ,('9','30 - Aplicación de anticipos') ,('22','30 - Aplicación de anticipos') ,('8','99 - Por definir')], string = "Forma de pago",track_visibility='onchange')

    banco = fields.Selection([('268',' - BNM840515VB1') ,('782',' - BNM840515VB1') ,('527',' - ') ,('553',' - ') ,('813',' - 12799.44') ,('816',' - SIN9412025I4') ,('817',' - SIN9412025I4') ,('568',' - ') ,('590',' - ') ,('679',' - ') ,('681',' - ') ,('695',' - ') ,('9','BAJIO - BBA940707IE1') ,('602','BAJIO - BBA940707IE1') ,('623','BAJIO - BBA940707IE1') ,('180','BAJIO - BBA940707IE1') ,('181','BAJIO - BBA940707IE1') ,('182','BAJIO - BBA940707IE1') ,('352','BANAM - BNM840515VB1') ,('517','BANAMEX - BNM840515VB1') ,('263','BANAMEX - BNM840515VB1') ,('8','BANAMEX - BNM840515VB1') ,('520','BANAMEX - BNM840515VB1') ,('265','BANAMEX - BNM840515VB1 ') ,('779','BANAMEX - ') ,('780','BANAMEX - BNM840515VB1 ') ,('269','BANAMEX - BNM840515VB1') ,('781','BANAMEX - BNM840515VB1') ,('270','BANAMEX - BNM840515VB1 ') ,('526','BANAMEX - BNM840515VB1') ,('15','BANAMEX - BNM840515VB1') ,('16','BANAMEX - BNM840515VB1') ,('784','BANAMEX - ') ,('18','BANAMEX - BNM840515VB1') ,('530','BANAMEX - BNM840515VB1') ,('19','BANAMEX - BNM840515VB1') ,('790','BANAMEX - BNM840515VB1') ,('26','BANAMEX - BNM840515VB1') ,('28','BANAMEX - BNM840515VB1') ,('284','BANAMEX - BNM840515VB1') ,('29','BANAMEX - BNM840515VB1') ,('285','BANAMEX - BNM840515VB1') ,('31','BANAMEX - BNM840515VB1') ,('32','BANAMEX - BNM840515VB1') ,('800','BANAMEX - ') ,('33','BANAMEX - BNM840515VB1') ,('291','BANAMEX - BNM840515VB1') ,('292','BANAMEX - BNM840515VB1') ,('548','BANAMEX - BNM840515VB1') ,('549','BANAMEX - BNM840515VB1') ,('552','BANAMEX - BNM840515VB1') ,('297','BANAMEX - BNM840515VB1 ') ,('298','BANAMEX - BNM840515VB1') ,('554','BANAMEX - BNM840515VB1') ,('555','BANAMEX - BNM840515VB1') ,('811','BANAMEX - BNM840515VB1') ,('558','BANAMEX - BNM840515VB1') ,('559','BANAMEX - BNM840515VB1') ,('305','BANAMEX - BNM840515VB1') ,('307','BANAMEX - BNM840515VB1') ,('308','BANAMEX - BNM840515VB1') ,('309','BANAMEX - BNM840515VB1') ,('565','BANAMEX - ') ,('310','BANAMEX - BNM840515VB1') ,('311','BANAMEX - BNM840515VB1') ,('313','BANAMEX - BNM840515VB1') ,('314','BANAMEX - BNM840515VB1') ,('570','BANAMEX - BNM840515VB1') ,('61','BANAMEX - BNM840515VB1') ,('317','BANAMEX - BNM840515VB1') ,('319','BANAMEX - BNM840515VB1') ,('577','BANAMEX - BNM840515VB1') ,('582','BANAMEX - BNM840515VB1') ,('329','BANAMEX - BNM840515VB1') ,('330','BANAMEX - BNM840515VB1') ,('76','BANAMEX - BNM840515VB1') ,('332','BANAMEX - BNM840515VB1') ,('77','BANAMEX - BNM840515VB1') ,('333','BANAMEX - BNM840515VB1') ,('78','BANAMEX - BNM840515VB1') ,('79','BANAMEX - BNM840515VB1') ,('80','BANAMEX - BNM840515VB1') ,('81','BANAMEX - BNM840515VB1') ,('338','BANAMEX - BNM840515VB1') ,('595','BANAMEX - BNM840515VB1') ,('85','BANAMEX - BNM840515VB1') ,('597','BANAMEX - BNM840515VB1') ,('342','BANAMEX - BNM840515VB1') ,('598','BANAMEX - BNM840515VB1') ,('599','BANAMEX - BNM840515VB1') ,('88','BANAMEX - BNM840515VB1') ,('600','BANAMEX - BNM840515VB1') ,('89','BANAMEX - BNM840515VB1') ,('90','BANAMEX - BNM840515VB1') ,('91','BANAMEX - BNM840515VB1') ,('98','BANAMEX - BNM840515VB1') ,('99','BANAMEX - ') ,('355','BANAMEX - BNM840515VB1') ,('100','BANAMEX - BNM840515VB1') ,('356','BANAMEX - BNM840515VB1') ,('101','BANAMEX - BNM840515VB1') ,('357','BANAMEX - BNM840515VB1 ') ,('358','BANAMEX - BNM840515VB1') ,('614','BANAMEX - BNM840515VB1') ,('359','BANAMEX - ') ,('106','BANAMEX - BNM840515VB1') ,('108','BANAMEX - BNM840515VB1') ,('109','BANAMEX - BNM840515VB1 ') ,('365','BANAMEX - BNM840515VB') ,('621','BANAMEX - BNM840515VB1') ,('622','BANAMEX - BNM840515VB1') ,('625','BANAMEX - BNM840515VB1') ,('370','BANAMEX - ') ,('626','BANAMEX - BNM840515VB1') ,('372','BANAMEX - ') ,('376','BANAMEX - BNM840515VB1') ,('127','BANAMEX - BNM840515VB1') ,('383','BANAMEX - BNM840515VB1') ,('128','BANAMEX - BNM840515VB1') ,('384','BANAMEX - BNM840515VB1') ,('640','BANAMEX - BNM840515VB1') ,('641','BANAMEX - BNM840515VB1') ,('642','BANAMEX - BNM840515VB1') ,('643','BANAMEX - BNM840515VB1') ,('389','BANAMEX - BNM840515VB1') ,('135','BANAMEX - BNM840515VB1') ,('647','BANAMEX - BNM840515VB1') ,('393','BANAMEX - BNM840515VB1') ,('649','BANAMEX - BNM840515VB1') ,('650','BANAMEX - BNM840515VB1') ,('141','BANAMEX - BNM840515VB1') ,('143','BANAMEX - BNM840515VB1') ,('144','BANAMEX - BNM840515VB1') ,('146','BANAMEX - BNM840515VB1') ,('149','BANAMEX - ') ,('405','BANAMEX - BNM840515VB1') ,('150','BANAMEX - ') ,('663','BANAMEX - BNM840515VB1') ,('419','BANAMEX - BNM840515VB1') ,('423','BANAMEX - ') ,('424','BANAMEX - BNM840515VB1') ,('426','BANAMEX - BNM840515VB1') ,('173','BANAMEX - BNM840515VB1') ,('429','BANAMEX - BNM840515VB1') ,('174','BANAMEX - BNM840515VB1 ') ,('430','BANAMEX - BNM840515VB1') ,('686','BANAMEX - BNM840515VB1') ,('175','BANAMEX - BNM840515VB1') ,('176','BANAMEX - BNM840515VB1') ,('178','BANAMEX - BNM840515VB1 ') ,('434','BANAMEX - BNM840515VB1') ,('691','BANAMEX - BNM840515VB1') ,('692','BANAMEX - BNM840515VB1') ,('445','BANAMEX - BNM840515VB1') ,('701','BANAMEX - BNM840515VB1') ,('191','BANAMEX - ') ,('703','BANAMEX - BNM840515VB1') ,('192','BANAMEX - BNM840515VB1') ,('196','BANAMEX - BNM840515VB1') ,('709','BANAMEX - BNM840515VB1') ,('710','BANAMEX - ') ,('711','BANAMEX - BNM840515VB1') ,('203','BANAMEX - BNM840515VB1') ,('204','BANAMEX - BNM840515VB1') ,('462','BANAMEX - BNM840515VB1') ,('208','BANAMEX - BNM840515VB1') ,('210','BANAMEX - BNM840515VB1') ,('466','BANAMEX - BNM840515VB1') ,('723','BANAMEX - BNM840515VB1') ,('212','BANAMEX - BNM840515VB1') ,('468','BANAMEX - BNM840515VB1') ,('214','BANAMEX - BNM840515VB1') ,('217','BANAMEX - BNM840515VB1') ,('731','BANAMEX - BNM840515VB1') ,('732','BANAMEX - BNM840515VB1') ,('222','BANAMEX - BNM840515VB1') ,('478','BANAMEX - BNM840515VB1') ,('224','BANAMEX - BNM840515VB1') ,('225','BANAMEX - BNM840515VB1') ,('226','BANAMEX - BNM840515VB1') ,('229','BANAMEX - BNM840515VB1') ,('741','BANAMEX - BNM840515VB1') ,('486','BANAMEX - BNM840515VB1') ,('742','BANAMEX - BNM840515VB1') ,('743','BANAMEX - ') ,('233','BANAMEX - BNM840515VB1') ,('489','BANAMEX - BNM840515VB1') ,('234','BANAMEX - BNM840515VB1') ,('235','BANAMEX - BNM840515VB1') ,('494','BANAMEX - BNM840515VB1') ,('754','BANAMEX - BNM840515VB1') ,('499','BANAMEX - BNM840515VB1') ,('755','BANAMEX - BNM840515VB1') ,('244','BANAMEX - BNM840515VB1') ,('756','BANAMEX - BNM840515VB1') ,('757','BANAMEX - BNM840515VB1') ,('502','BANAMEX - BNM840515VB1') ,('758','BANAMEX - ') ,('503','BANAMEX - BNM840515VB1') ,('504','BANAMEX - BNM840515VB1') ,('251','BANAMEX - BNM840515VB1') ,('764','BANAMEX - ') ,('766','BANAMEX - BNM840515VB') ,('767','BANAMEX - ') ,('27','BANBAJIO - BBA940707IE1') ,('795','BANBAJIO - BBA940707IE1') ,('92','BANBAJIO - BBA940707IE1') ,('93','BANBAJIO - BBA940707IE1') ,('675','BANBAJIO - BBA940707IE1') ,('381','BANCA MIFEL - BMI9312038R3') ,('696','BANCO AZTECA - BAI0205236Y8') ,('697','BANCO AZTECA - BAI0205236Y8') ,('253','BANCO BASE - BBS110906HD3') ,('563','BANCO DEL BAJÍO - BBA940707IE1') ,('316','BANCO DEL BAJÍO - BBA940707IE1') ,('318','BANCO DEL BAJÍO - BBA940707IE1') ,('606','BANCO DEL BAJÍO - BBA940707IE1') ,('607','BANCO DEL BAJÍO - BBA940707IE1') ,('608','BANCO DEL BAJÍO - BBA940707IE1') ,('387','BANCO DEL BAJÍO - BBA940707IE1') ,('398','BANCO DEL BAJÍO - BBA940707IE1') ,('399','BANCO DEL BAJÍO - BBA940707IE1') ,('402','BANCO DEL BAJÍO - BBA940707IE1') ,('416','BANCO DEL BAJÍO - BBA940707IE1') ,('417','BANCO DEL BAJÍO - BBA940707IE1') ,('529','BANCO DEL BAJIO SA - BBA940707IE1') ,('379','BANCO J.P. MORGAN S.A. - BJP-950104-LJ') ,('380','BANCO J.P. MORGAN S.A. - BJP950104LJ5') ,('408','BANCO J.P. MORGAN S.A. - BJP950104LJ5') ,('409','BANCO J.P. MORGAN S.A. - BJP950104LJ5') ,('159','BANCO J.P. MORGAN S.A. - BJP-950104-LJ') ,('45','BANCO J.P.MORGAN SA - BJP950104LJ5') ,('165','BANCO J.P.MORGAN SA - BJP950104LJ5') ,('615','Banco Mercantil del Norte - BMN930209927') ,('129','Banco Mercantil del Norte - BMN930209927') ,('131','Banco Mercantil del Norte - BMN930209927') ,('213','BANCO MERCANTIL DEL NORTE - BMN930209927') ,('55','BANCO MERCANTIL DEL NORTE S.A. - BMN930209-927') ,('56','BANCO MERCANTIL DEL NORTE S.A. - BMN930209927') ,('280','BANCO MULTIVA, SA - BMI061005NY5') ,('281','BANCO MULTIVA, SA - BMI061005NY5') ,('282','BANCO MULTIVA, SA - BMI061005NY5') ,('651','BANCO REGIONAL DE MONTERREY S.A. - BRM940216EQ6') ,('267','BANCO SANTANDER - BSM970519DU8') ,('474','BANCO SANTANDER - BSM970519DU8') ,('266','BANCO SANTANDER (MEXICO) S.A., INSTITUCION DE BANC - BSM970519DU8') ,('152','BANCO SANTANDER (MEXICO) SA - BSM970519DU8') ,('261','BANCO VE POR MAS - BVM951002LX0') ,('258','BANCOMER - BBA830831LJ2') ,('13','BANCOMER - BBA830831LJ2') ,('531','BANCOMER - BBA830831LJ2') ,('20','BANCOMER - BBA830831LJ2') ,('277','BANCOMER - BBA830831LJ2') ,('23','BANCOMER - BBA830831LJ2') ,('24','BANCOMER - BBA830831LJ2') ,('542','BANCOMER - BBA830831LJ2') ,('288','BANCOMER - BBA830831LJ2') ,('289','BANCOMER - BBA830831LJ2') ,('545','BANCOMER - BBA830831LJ2') ,('34','BANCOMER - BBA830831LJ2') ,('290','BANCOMER - BBA830831LJ2') ,('35','BANCOMER - BBA830831LJ2') ,('36','BANCOMER - BBA830831LJ2') ,('293','BANCOMER - BBA830831LJ2') ,('39','BANCOMER - BBA830831LJ2') ,('40','BANCOMER - BBA830831LJ2') ,('41','BANCOMER - BBA830831LJ2') ,('569','BANCOMER - BBA830831LJ2') ,('60','BANCOMER - BBA830831LJ2') ,('572','BANCOMER - BBA830831LJ2') ,('62','BANCOMER - BBA830831LJ2') ,('575','BANCOMER - BBA830831LJ2') ,('65','BANCOMER - BBA830831LJ2') ,('321','BANCOMER - BBA830831LJ2') ,('68','BANCOMER - BBA830831LJ2') ,('580','BANCOMER - BBA830831LJ2') ,('72','BANCOMER - BBA830831LJ2') ,('75','BANCOMER - BBA830831LJ2') ,('334','BANCOMER - BBA830831LJ2') ,('351','BANCOMER - BBA830831LJ2') ,('103','BANCOMER - BBA830831LJ2') ,('104','BANCOMER - BBA830831LJ2') ,('105','BANCOMER - BBA830831LJ2') ,('361','BANCOMER - BBA830831LJ2') ,('362','BANCOMER - BBA830831LJ2') ,('107','BANCOMER - BBA830831LJ2') ,('363','BANCOMER - BBA830831LJ2') ,('364','BANCOMER - BBA830831LJ2') ,('367','BANCOMER - BBA830831LJ2') ,('113','BANCOMER - BBA830831LJ2') ,('369','BANCOMER - BBA830831LJ2') ,('117','BANCOMER - BBA830831LJ2') ,('118','BANCOMER - BBA830831LJ2') ,('377','BANCOMER - BBA830831LJ2') ,('378','BANCOMER - BBA830831LJ2') ,('635','BANCOMER - BBA830831LJ2') ,('636','BANCOMER - BBA830831LJ2') ,('639','BANCOMER - BBA830831LJ2') ,('134','BANCOMER - BBA830831LJ2') ,('390','BANCOMER - BBA830831LJ2') ,('392','BANCOMER - BBA830831LJ2') ,('137','BANCOMER - BBA830831LJ2') ,('138','BANCOMER - BBA830831LJ2') ,('140','BANCOMER - BBA830831LJ2') ,('403','BANCOMER - BBA830831LJ2') ,('661','BANCOMER - BBA830831LJ2') ,('662','BANCOMER - BBA830831LJ2') ,('158','BANCOMER - BBA830831LJ2') ,('414','BANCOMER - BBA830831LJ2') ,('415','BANCOMER - BBA830831LJ2') ,('422','BANCOMER - BBA830831LJ2') ,('427','BANCOMER - BBA830831LJ2') ,('428','BANCOMER - BBA830831LJ2') ,('183','BANCOMER - BBA830831LJ2') ,('186','BANCOMER - BBA830831LJ2') ,('704','BANCOMER - BBA830831LJ2') ,('458','BANCOMER - BBA830831LJ2') ,('716','BANCOMER - BBA830831LJ2') ,('216','BANCOMER - BBA830831LJ2') ,('473','BANCOMER - BBA830831LJ2') ,('218','BANCOMER - BBA830831LJ2') ,('475','BANCOMER - BBA830831LJ2') ,('221','BANCOMER - BBA830831LJ2') ,('477','BANCOMER - BBA830831LJ2') ,('736','BANCOMER - BBA830831LJ2') ,('737','BANCOMER - BBA830831LJ2') ,('739','BANCOMER - BBA830831LJ2') ,('740','BANCOMER - ') ,('230','BANCOMER - BBA830831LJ2') ,('231','BANCOMER - BBA830831LJ2') ,('490','BANCOMER - BBA830831LJ2') ,('751','BANCOMER - BBA830831LJ2') ,('241','BANCOMER - BBA830831LJ2') ,('497','BANCOMER - BBA830831LJ2') ,('243','BANCOMER - BBA830831LJ2') ,('501','BANCOMER - BBA830831LJ2') ,('507','BANCOMER - BBA830831LJ2') ,('509','BANCOMER - BBA830831LJ2') ,('666','BANCONER - BBA830831LJ2') ,('534','BANK OF AMERICA MEXICO - ') ,('341','BANK OF AMERICA MEXICO - BAM9504035J2') ,('343','BANK OF AMERICA MEXICO - BAM9504035J2') ,('344','BANK OF AMERICA MEXICO - BAM9504035J2') ,('345','BANK OF AMERICA MEXICO - BAM9504035J2') ,('346','BANK OF AMERICA MEXICO - BAM9504035J2') ,('656','BANK OF AMERICA MEXICO - ') ,('657','BANK OF AMERICA MEXICO - BAM9504035J2') ,('706','BANK OF AMERICA MEXICO - BAM9504035J2') ,('773','BANORTE - EOP510101UA4') ,('774','BANORTE - EOP510101UA4') ,('775','BANORTE - EOP510101UA4') ,('17','BANORTE - BMN930209927') ,('276','BANORTE - BMN930209927') ,('794','BANORTE - BMN930209927') ,('540','BANORTE - BMN930209927') ,('541','BANORTE - BMN930209927') ,('797','BANORTE - BMN930209927 ') ,('798','BANORTE - BMN930209927 ') ,('543','BANORTE - BMN930209927') ,('799','BANORTE - BMN930209927') ,('544','BANORTE - BMN930209927') ,('801','BANORTE - ') ,('37','BANORTE - BMN930209927') ,('805','BANORTE - BMN930209927') ,('550','BANORTE - BMN930209927') ,('806','BANORTE - BMN930209927') ,('551','BANORTE - BMN930209927') ,('807','BANORTE - BMN930209927') ,('299','BANORTE - BMN930209927') ,('300','BANORTE - BMN930209927') ,('301','BANORTE - BMN930209927') ,('46','BANORTE - BMN930299277') ,('47','BANORTE - ') ,('48','BANORTE - ') ,('49','BANORTE - BMN930209927') ,('561','BANORTE - BMN930209927') ,('564','BANORTE - BMN930209927') ,('54','BANORTE - BMN930209927') ,('567','BANORTE - BMN930209927') ,('57','BANORTE - BMN930209927') ,('58','BANORTE - BMN930209927') ,('59','BANORTE - BMN930209927') ,('320','BANORTE - BMN930209927') ,('66','BANORTE - BMN930209927') ,('322','BANORTE - BMN930209927') ,('71','BANORTE - BMN930209927') ,('592','BANORTE - BMN930209927') ,('593','BANORTE - BMN930209927') ,('596','BANORTE - BMN930209927') ,('601','BANORTE - BMN930209927') ,('347','BANORTE - BMN930209927') ,('603','BANORTE - BMN930209927') ,('605','BANORTE - BMN930209927') ,('95','BANORTE - BMN930209927') ,('353','BANORTE - BMN930209927') ,('610','BANORTE - BMN930209927') ,('619','BANORTE - BMN930209927') ,('368','BANORTE - BMN930209927') ,('634','BANORTE - BMN930209927') ,('126','BANORTE - ') ,('388','BANORTE - BMN930209927') ,('391','BANORTE - BMN930209927') ,('658','BANORTE - BMN930209927') ,('147','BANORTE - BMN930209927') ,('660','BANORTE - BMN930209927') ,('406','BANORTE - BMN930209927') ,('665','BANORTE - BMN930209927') ,('155','BANORTE - BMN930209927') ,('156','BANORTE - BMN930209927') ,('669','BANORTE - BMN930209927') ,('670','BANORTE - BMN930209927') ,('671','BANORTE - BMN930209927') ,('672','BANORTE - BMN930209927') ,('677','BANORTE - BMN930209927') ,('688','BANORTE - BMN930209927') ,('436','BANORTE - BMN930209927') ,('438','BANORTE - BMN930209927') ,('439','BANORTE - BMN930209927') ,('185','BANORTE - BMN930209927') ,('187','BANORTE - BMN930209 927') ,('188','BANORTE - BMN930209927') ,('190','BANORTE - BMN930209927') ,('702','BANORTE - BMN930209927') ,('447','BANORTE - BMN930209927') ,('448','BANORTE - BMN930209927') ,('449','BANORTE - BMN930209927') ,('451','BANORTE - BMN930209927') ,('707','BANORTE - BMN930209927') ,('457','BANORTE - BMN930209927') ,('714','BANORTE - BMN930209927') ,('718','BANORTE - BMN930209927') ,('463','BANORTE - BMN930209927') ,('721','BANORTE - BMN930209927') ,('722','BANORTE - BMN930209927 ') ,('470','BANORTE - BMN930209927') ,('215','BANORTE - BMN930209927') ,('220','BANORTE - BMN930209927') ,('733','BANORTE - BMN930209927') ,('735','BANORTE - BMN930209927') ,('738','BANORTE - BMN930209927') ,('485','BANORTE - BMN930209927') ,('747','BANORTE - ') ,('237','BANORTE - BMN930209927') ,('238','BANORTE - BMN930209927') ,('496','BANORTE - BMN930209927') ,('753','BANORTE - BMN930209927') ,('242','BANORTE - BMN930209927') ,('500','BANORTE - BMN930209927') ,('759','BANORTE - BMN930209927') ,('760','BANORTE - BMN930209927 ') ,('761','BANORTE - BMN930209927') ,('250','BANORTE - BMN930209927') ,('762','BANORTE - ') ,('532','BANREGIO - BRM940216EQ6') ,('360','BANREGIO - BRM940216EQ6') ,('768','BBVA BANCOMER - BBA830831LJ2') ,('769','BBVA BANCOMER - BBA830831LJ2') ,('771','BBVA BANCOMER - BBA830831LJ2') ,('260','BBVA BANCOMER - BBA830831LJ2') ,('772','BBVA BANCOMER - BBA830831LJ2') ,('262','BBVA BANCOMER - BBA830831LJ2') ,('518','BBVA BANCOMER - BBA830831LJ2') ,('522','BBVA BANCOMER - BBA830831LJ2') ,('14','BBVA BANCOMER - BBA830831LJ2') ,('271','BBVA BANCOMER - BBA830831LJ2') ,('272','BBVA BANCOMER - BBA830831LJ2') ,('273','BBVA BANCOMER - BBA830831LJ2') ,('274','BBVA BANCOMER - BBA830831LJ2') ,('275','BBVA BANCOMER - BBA830831LJ2') ,('793','BBVA BANCOMER - BBA830831LJ2') ,('283','BBVA BANCOMER - BBA830831LJ2') ,('286','BBVA BANCOMER - BBA830831LJ2') ,('547','BBVA BANCOMER - BBA830831LJ2') ,('803','BBVA BANCOMER - BBA830831LJ2') ,('294','BBVA BANCOMER - BBA830831LJ2') ,('296','BBVA BANCOMER - BBA830831LJ2') ,('302','BBVA BANCOMER - BBA830831LJ2') ,('303','BBVA BANCOMER - BBA830831LJ2') ,('815','BBVA BANCOMER - BBA830831LJ2') ,('304','BBVA BANCOMER - BBA830831LJ2') ,('306','BBVA BANCOMER - BBA830831LJ2') ,('562','BBVA Bancomer - BBA830831LJ2') ,('819','BBVA BANCOMER - BBA830831LJ2') ,('53','BBVA BANCOMER - BBA830831LJ2') ,('315','BBVA BANCOMER - BBA830831LJ2') ,('571','BBVA BANCOMER - BBA830831LJ2') ,('573','BBVA BANCOMER - BBA830831LJ2') ,('574','BBVA BANCOMER - BBA830831LJ2') ,('576','BBVA BANCOMER - BBA830831LJ2') ,('581','BBVA Bancomer - BBA830831LJ2') ,('326','BBVA BANCOMER - BBA830831LJ2') ,('327','BBVA BANCOMER - BBA830831LJ2') ,('328','BBVA BANCOMER - BBA830831LJ2') ,('331','BBVA BANCOMER - BBA830831LJ2') ,('335','BBVA BANCOMER - BBA830831LJ2') ,('337','BBVA BANCOMER - BBA830831LJ2') ,('82','BBVA BANCOMER - BBA830831LJ2') ,('594','BBVA BANCOMER - BBA830831LJ2') ,('83','BBVA BANCOMER - BBA830831LJ2') ,('339','BBVA BANCOMER - BBA830831LJ2') ,('84','BBVA BANCOMER - BBA830831LJ2') ,('340','BBVA BANCOMER - BBA830831LJ2') ,('86','BBVA BANCOMER - BBA830831LJ2') ,('87','BBVA BANCOMER - BBA830831LJ2') ,('94','BBVA BANCOMER - BBA830831LJ2') ,('609','BBVA BANCOMER - BBA830831LJ2') ,('611','BBVA BANCOMER - BBA830831LJ2') ,('617','BBVA BANCOMER - BBA830831LJ2') ,('618','BBVA BANCOMER - BBA830831LJ2') ,('620','BBVA BANCOMER - BBA830831LJ2') ,('624','BBVA BANCOMER - BBA830831LJ2') ,('114','BBVA BANCOMER - ') ,('627','BBVA BANCOMER - BBA830831LJ2') ,('628','BBVA BANCOMER - BBA830831LJ2') ,('629','BBVA Bancomer - BBA830831LJ2') ,('374','BBVA BANCOMER - BBA830831LJ2') ,('630','BBVA Bancomer - BBA830831LJ2') ,('631','BBVA Bancomer - BBA830831LJ2') ,('633','BBVA BANCOMER - BBA830831LJ2') ,('122','BBVA BANCOMER - BBA830831LJ2') ,('123','BBVA BANCOMER - BBA830831LJ2') ,('638','BBVA BANCOMER - BBA830831LJ2') ,('132','BBVA BANCOMER - BBA830831LJ2') ,('644','BBVA BANCOMER - BBA830831LJ2') ,('133','BBVA BANCOMER - BBA830831LJ2') ,('645','BBVA BANCOMER - BBA830831LJ2') ,('136','BBVA Bancomer - BBA830831LJ2') ,('648','BBVA BANCOMER - BBA830831LJ2') ,('394','BBVA BANCOMER - BBA830831LJ2') ,('397','BBVA BANCOMER - BBA830831LJ2') ,('653','BBVA BANCOMER - BBA830831LJ2') ,('142','BBVA BANCOMER - BBA830831LJ2') ,('654','BBVA Bancomer - BBA830831LJ2') ,('659','BBVA BANCOMER - BBA830831LJ2') ,('148','BBVA BANCOMER - BBA830831LJ2') ,('151','BBVA BANCOMER - BBA830831LJ2') ,('664','BBVA BANCOMER - BBA830831LJ2') ,('154','BBVA BANCOMER - BBA830831LJ2') ,('410','BBVA BANCOMER - BBA830831LJ2') ,('411','BBVA Bancomer - BBA830831LJ2') ,('412','BBVA BANCOMER - BBA830831LJ2') ,('162','BBVA BANCOMER - BBA830831LJ2') ,('418','BBVA BANCOMER - BBA830831LJ2') ,('163','BBVA BANCOMER - BBA830831LJ2') ,('420','BBVA BANCOMER - BBA830831LJ2') ,('676','BBVA Bancomer - BBA830831LJ2') ,('421','BBVA BANCOMER - BBA830831LJ2') ,('172','BBVA BANCOMER - BBA830831LJ2') ,('431','BBVA Bancomer - BBA830831LJ2') ,('687','BBVA BANCOMER - BBA830831LJ2') ,('432','BBVA BANCOMER - BBA830831LJ2') ,('177','BBVA BANCOMER - BBA830831LJ2') ,('433','BBVA BANCOMER - BBA830831LJ2') ,('690','BBVA BANCOMER - BBA830831LJ2') ,('694','BBVA BANCOMER - BBA830831LJ2') ,('444','BBVA BANCOMER - BBA830831LJ2') ,('189','BBVA Bancomer - BBA830831LJ2') ,('193','BBVA BANCOMER - BBA830831LJ2') ,('450','BBVA BANCOMER - BBA830831LJ2') ,('452','BBVA BANCOMER - BBA830831LJ2') ,('708','BBVA BANCOMER - BBA830831LJ2') ,('197','BBVA BANCOMER - BBA830831LJ2') ,('198','BBVA BANCOMER - BBA830831LJ2') ,('199','BBVA BANCOMER - BBA830831LJ2') ,('455','BBVA BANCOMER - BBA830831LJ2') ,('456','BBVA BANCOMER - BBA830831LJ2') ,('201','BBVA BANCOMER - BBA830831LJ2') ,('713','BBVA Bancomer - BBA830831LJ2') ,('202','BBVA BANCOMER - BBA830831LJ2') ,('205','BBVA BANCOMER - BBA830831LJ2') ,('206','BBVA BANCOMER - BBA830831LJ2') ,('209','BBVA BANCOMER - BBA830831LJ2') ,('469','BBVA BANCOMER - BBA830831LJ2') ,('472','BBVA BANCOMER - BBA830831LJ2') ,('728','BBVA BANCOMER - BBA830831LJ2') ,('729','BBVA Bancomer - BBA830831LJ2') ,('730','BBVA BANCOMER - BBA830831LJ2') ,('734','BBVA BANCOMER - BBA830831LJ2') ,('479','BBVA BANCOMER - BBA830831LJ2') ,('480','BBVA BANCOMER - BBA830831LJ2') ,('481','BBVA BANCOMER - BBA830831LJ2') ,('482','BBVA BANCOMER - BBA830831LJ2') ,('483','BBVA BANCOMER - BBA830831LJ2') ,('484','BBVA BANCOMER - BBA830831LJ2') ,('487','BBVA Bancomer - BBA830831LJ2') ,('488','BBVA Bancomer - BBA830831LJ2') ,('744','BBVA BANCOMER - BBA830831LJ2') ,('746','BBVA BANCOMER - BBA830831LJ2') ,('493','BBVA BANCOMER - BBA830831LJ2') ,('749','BBVA BANCOMER - BBA830831LJ2') ,('750','BBVA BANCOMER - BBA830831LJ2') ,('495','BBVA BANCOMER - BBA830831LJ2') ,('752','BBVA BANCOMER - BBA830831LJ2') ,('245','BBVA BANCOMER - BBA830831LJ2') ,('246','BBVA BANCOMER - BBA830831LJ2') ,('247','BBVA BANCOMER - BBA830831LJ2') ,('249','BBVA BANCOMER - BBA830831LJ2') ,('508','BBVA BANCOMER - BBA830831LJ2') ,('765','BBVA BANCOMER - BBA830831LJ2') ,('804','BBVA Bancomer, S.A. - BBA830831LJ2') ,('10','CI BANCO - BCI001030ECA') ,('700','CI BANCO - CIB850918BN') ,('207','CI BANCO - BNY080206UR9') ,('278','CITI BANAMEX - BNM840515VB1') ,('279','CITI BANAMEX - BNM840515VB1') ,('513','HSBC - HMI950125KG8') ,('519','HSBC - HMI950125KG8') ,('776','HSBC - HMI950125KG8') ,('525','HSBC - HMI950125KG8') ,('783','HSBC - HMI950125KG8') ,('533','HSBC - HMI950125KG8') ,('25','HSBC - HMI950125KG8') ,('802','HSBC - ') ,('556','HSBC - HMI950125KG8') ,('323','HSBC - HSBC046722') ,('325','HSBC - ') ,('96','HSBC - HMI950125KG8') ,('97','HSBC - HMI950125KG8') ,('386','HSBC - HMI950125KG8') ,('667','HSBC - HMI950125KG8') ,('160','HSBC - HMI950125KG8') ,('166','HSBC - HMI950125KG8') ,('685','HSBC - HMI950125KG8') ,('693','HSBC - HMI950125KG8') ,('719','HSBC - HMI950125KG8') ,('465','HSBC - HMI950125KG8') ,('471','HSBC - HMI950125KG8') ,('227','HSBC - HMI950125KG8') ,('252','HSBC - HMI950125KG8') ,('295','HSBC . - HMI950125KG8') ,('777','HSBC MEXICO S.A. - HMI-950125KG8') ,('778','HSBC MEXICO S.A. - HMI950125KG8') ,('812','HSBC MEXICO S.A. - HMI950125KG8') ,('557','HSBC MEXICO S.A. - HMI950125KG8') ,('818','HSBC MEXICO S.A. - ASC960408K10') ,('110','HSBC MEXICO S.A. - ASC960408K10') ,('111','HSBC MEXICO S.A. - ASC960408K10') ,('112','HSBC MEXICO S.A. - ASC960408K10') ,('652','HSBC MEXICO S.A. - HMI950125KG8') ,('157','HSBC MEXICO S.A. - HMI-950125KG8') ,('184','HSBC MEXICO S.A. - ') ,('232','HSBC MEXICO S.A. - HMI950125KG8') ,('259','INBURSA - BII931004P61') ,('67','INBURSA - BII931004P61') ,('354','INBURSA - BII931004P61') ,('616','INBURSA - BII931004P61') ,('366','INBURSA - BII931004P61') ,('115','INBURSA - BII931004P61') ,('116','INBURSA - BII931004P61') ,('119','INBURSA - FCS890710CW5') ,('120','INBURSA - FCS890710CW5') ,('130','INBURSA - BII931004P61') ,('646','INBURSA - BII931004P61') ,('161','INBURSA - BII931004P61') ,('254','INBURSA - BII931004P61') ,('255','INBURSA - BII931004P61') ,('264','INVERLAT - SIN9412025I4') ,('791','J P MORGAN - BJP950104LJ5') ,('792','J P MORGAN - BJP950104LJ5') ,('385','J P MORGAN - XEXX010101000') ,('395','J P MORGAN - BJP950104LJ5') ,('400','J P MORGAN - BJP950104LJ5') ,('698','J P MORGAN - BJP950104LJ5') ,('348','MONEX - BMI9704113PA') ,('632','MONEX - BMI9704113PA') ,('699','MONEX - BMI9704113PA') ,('453','MONEX - BMI9704113PA') ,('11','MULTIVA - BMI061005NY5') ,('324','MULTIVA - BMI061005NY5') ,('239','MULTIVA - BMI061005NYS') ,('240','MULTIVA - BMI061005NY5') ,('256','SANTANDER - BSM970519DU8') ,('512','SANTANDER - BSM970519DU8') ,('257','SANTANDER - BSM970519DU8') ,('514','SANTANDER - BSM970519DU8') ,('770','SANTANDER - BSM970519DU8') ,('515','SANTANDER - BSM970519DU8') ,('516','SANTANDER - BSM970519DU8') ,('521','SANTANDER - BSM970519DU8') ,('523','SANTANDER - BSM970519DU8') ,('12','SANTANDER - BSM970519DU8') ,('524','SANTANDER - BSM970519DU8') ,('528','SANTANDER - BSM970519DU8') ,('785','SANTANDER - BSM970519DU8') ,('786','SANTANDER - BSM970519DU8') ,('787','SANTANDER - BSM970519DU8') ,('788','SANTANDER - BSM970519DU8') ,('21','SANTANDER - BSM970519DU8') ,('789','SANTANDER - BSM970519DU8') ,('22','SANTANDER - BSM970519DU8') ,('535','SANTANDER - BSM970519DU8') ,('536','SANTANDER - BSM970519DU8') ,('537','SANTANDER - BSM970519DU8') ,('538','SANTANDER - BSM970519DU8') ,('30','SANTANDER - BSM970519DU8') ,('287','SANTANDER - BSM970519DU8') ,('546','SANTANDER - BSM970519DU8') ,('38','SANTANDER - BSM970519DU8') ,('809','SANTANDER - XEXX010101000') ,('42','SANTANDER - BSM970519DU8') ,('810','SANTANDER - BSM970519DU8') ,('43','SANTANDER - BSM970519DU8') ,('44','SANTANDER - BSM970519DU8') ,('814','SANTANDER - BSM970519DU8') ,('560','SANTANDER - BSM970519DU8') ,('50','SANTANDER - BSM970519DU8') ,('51','SANTANDER - BSM970519DU8') ,('52','SANTANDER - BSM970519DU8') ,('63','SANTANDER - BSM970519DU8') ,('64','SANTANDER - BSM970519DU8') ,('69','SANTANDER - BSM970519DU8') ,('70','SANTANDER - BSM970519DU8') ,('73','SANTANDER - BSM970519DU8') ,('74','SANTANDER - BSM970519DU8') ,('589','SANTANDER - BSM970519DU8') ,('591','SANTANDER - BSM970519DU8') ,('336','SANTANDER - BSM970519DU8') ,('349','SANTANDER - BSM970519DU8') ,('350','SANTANDER - BSM970519DU8') ,('612','SANTANDER - BSM970519DU8') ,('613','SANTANDER - BSM970519DU8') ,('102','SANTANDER - BSM970519DU8') ,('371','SANTANDER - BSM970519DU8') ,('373','SANTANDER - SIN9412025I4') ,('375','SANTANDER - BSM970519DU8') ,('121','SANTANDER - BSM970519DU8') ,('124','SANTANDER - BSM970519DUB') ,('125','SANTANDER - BSM970519DU8') ,('637','SANTANDER - BSM970519DU8') ,('382','SANTANDER - BSM970519DU8') ,('139','SANTANDER - BSM970519DU8') ,('396','SANTANDER - BSM970519DU8') ,('655','SANTANDER - BSM970519DU8') ,('145','SANTANDER - BSM970519DU8') ,('407','SANTANDER - BSM970519DU8') ,('153','SANTANDER - BSM970519DU8') ,('668','SANTANDER - BSM970519DU8') ,('413','SANTANDER - ') ,('164','SANTANDER - BSM970519DU8') ,('678','SANTANDER - BSM970519DU8') ,('167','SANTANDER - BSM970519DU8') ,('168','SANTANDER - BSM970519DU8') ,('680','SANTANDER - ') ,('169','SANTANDER - BSM970519DU8') ,('425','SANTANDER - BSM970519DU8') ,('170','SANTANDER - BSM970519DU8') ,('682','SANTANDER - ') ,('683','SANTANDER - BMN930299277') ,('684','SANTANDER - BSM970519DU8') ,('689','SANTANDER - BSM970519DU8') ,('179','SANTANDER - BSM970519DU8') ,('435','SANTANDER - BSM970519DU8') ,('437','SANTANDER - BSM970519DU8') ,('440','SANTANDER - BSM970519DU8') ,('441','SANTANDER - BSM970519DU8') ,('442','SANTANDER - BSM970519DU8') ,('443','SANTANDER - BSM970519DU8') ,('446','SANTANDER - BSM970519DU8') ,('705','SANTANDER - BSM970519DU8') ,('194','SANTANDER - BSM970519DU8') ,('195','SANTANDER - BSM970519DU8') ,('454','SANTANDER - BSM970519DU8') ,('200','SANTANDER - BSM970519DU8') ,('712','SANTANDER - BSM970519DU8') ,('459','SANTANDER - BSM970519DU8') ,('715','SANTANDER - BSM970519DU8') ,('460','SANTANDER - BSM970519DU8') ,('461','SANTANDER - BSM970519DU8') ,('717','SANTANDER - BSM970519DU8') ,('720','SANTANDER - BSM970519DU8') ,('211','SANTANDER - BSM970519DU8') ,('467','SANTANDER - BSM970519DU8') ,('724','SANTANDER - BSM970519DU8') ,('725','SANTANDER - BSM970519DU8') ,('726','SANTANDER - BSM970519DU8') ,('727','SANTANDER - BSM970519DU8') ,('219','SANTANDER - BSM970519DU8') ,('476','SANTANDER - BSM970519DU8') ,('223','SANTANDER - BSM970519DU8') ,('228','SANTANDER - BSM970519DU8') ,('745','SANTANDER - BSM970519DU8') ,('491','SANTANDER - BSM970519DU8') ,('492','SANTANDER - BSM970519DU8') ,('498','SANTANDER - BSM970519DU8') ,('248','SANTANDER - BSM970519DU8') ,('505','SANTANDER - BSM970519DU8') ,('506','SANTANDER - BSM970519DU8') ,('763','SANTANDER - BSM970519DU8') ,('510','SANTANDER - BSM970519DU8') ,('511','SANTANDER - BSM970519DU8') ,('796','SCOTIABANK - SIN9412025I4') ,('808','SCOTIABANK - SIN9412025I4') ,('566','SCOTIABANK - SIN9412025I4') ,('312','SCOTIABANK - SIN9412025I4') ,('578','SCOTIABANK - SIN9412025I4') ,('579','SCOTIABANK - SIN9412025I4') ,('604','SCOTIABANK - SIN9412025I4') ,('404','SCOTIABANK - SIN9412025I4') ,('748','SCOTIABANK - SIN9412025I4') ,('673','SCOTIABANK INVERLAT SA - SIN9412025I4') ,('674','SCOTIABANK INVERLAT SA - SIN9412025I4') ,('583','Scotiabank Inverlat, S.A. - SIN9412025I4') ,('584','Scotiabank Inverlat, S.A. - SIN9412025I4') ,('585','Scotiabank Inverlat, S.A. - SIN9412025I4') ,('586','Scotiabank Inverlat, S.A. - SIN9412025I4') ,('587','Scotiabank Inverlat, S.A. - SIN9412025I4') ,('588','Scotiabank Inverlat, S.A. - SIN9412025I4') ,('401','Scotiabank Inverlat, S.A. - SIN9412025I4') ,('171','Scotiabank Inverlat, S.A. - SIN9412025I4') ,('464','SCOTIANBANK INVERLAT - SIN9412025I4')], string = "Banco",track_visibility='onchange')

    cuentaBancaria  = fields.Selection([('24','BAJIO - 9777600201 - MON NAC') ,('19','BANAMEX - 002180418300272792 - MONEDA NAC') ,('12','BANAMEX - 002180700725697152 - CHEQUES M.') ,('16','CI BANCO - 0001120336 - MONEDA NAC') ,('17','MULTIVA - 0004738918 - MONEDA NAC')], string = "Cuenta bancaria definida",track_visibility='onchange')
    
    metodPago = fields.Selection([('6','PPD Pago en parcialidades o diferido') ,('5','PUE Pago en una sola exhibición')], string = "Método de pago",track_visibility='onchange')
    numCuenta = fields.Integer(string="Número Cuenta",track_visibility='onchange')

    razonSocial  = fields.Selection([('1','SERVICIOS CORPORATIVOS GENESIS, S.A DE C.V.') ,('2','OUTSOURCING DIGITAL FRIENDLY, S.A. DE C.V.') ,('3" selected="','GN SYS CORPORATIVO S.A. DE C.V.') ,('1000','EMPRESA PRUEBAS CFDI') ,('1001','DOCUMENTO INTEGRAL CORPORATIVO, SA DE CV') ,('1002','GRUPO GNSYS SOLUCIONES SA DE CV')], string = "Razón Social",track_visibility='onchange')

    usoCFDI = fields.Selection([('12','D01 Honorarios médicos, dentales y gastos hospitalarios.') ,('13','D02 Gastos médicos por incapacidad o discapacidad') ,('14','D03 Gastos funerales.') ,('15','D04 Donativos.') ,('16','D05 Intereses reales efectivamente pagados por créditos hipotecarios (casa habitación).') ,('17','D06 Aportaciones voluntarias al SAR.') ,('18','D07 Primas por seguros de gastos médicos.') ,('19','D08 Gastos de transportación escolar obligatoria.') ,('20','D09 Depósitos en cuentas para el ahorro, primas que tengan como base planes de pensiones.') ,('21','D10 Pagos por servicios educativos (colegiaturas)') ,('1','G01 Adquisición de mercancias') ,('2','G02 Devoluciones, descuentos o bonificaciones') ,('3','G03 Gastos en general') ,('4','I01 Construcciones') ,('5','I02 Mobilario y equipo de oficina por inversiones') ,('6','I03 Equipo de transporte') ,('7','I04 Equipo de computo y accesorios') ,('8','I05 Dados, troqueles, moldes, matrices y herramental') ,('9','I06 Comunicaciones telefónicas') ,('10','I07 Comunicaciones satelitales') ,('11','I08 Otra maquinaria y equipo') ,('22','P01 Por definir')], string = "Uso CFDI",track_visibility='onchange')

    diasCredito = fields.Integer(string="Días de crédito",track_visibility='onchange')
    limbo  = fields.Boolean(string="Limbo", default=False)
    activo = fields.Boolean(string="Activo", default=False)
    #Dirección Fiscal
    
    calle        = fields.Char(string="Calle",track_visibility='onchange')
    colonia      = fields.Char(string="Colonia",track_visibility='onchange')    
    delegacion   = fields.Char(string="Delegación",track_visibility='onchange')  
    direcFactura = fields.Char(string="Este cliente factura a ",track_visibility='onchange')
    numExterior  = fields.Integer(string="No.exterior ",track_visibility='onchange')
    numInterior  = fields.Integer(string="No. interior ",track_visibility='onchange')
    estado       = fields.Selection([('Aguascalientes','Aguascalientes') ,('Baja California','Baja California') ,('Baja California Sur','Baja California Sur') ,('Campeche','Campeche') ,('Ciudad de México" ','Ciudad de México') ,('Coahuila','Coahuila') ,('Colima','Colima') ,('Chiapas','Chiapas') ,('Chihuahua','Chihuahua') ,('Durango','Durango') ,('Estado de México','Estado de México') ,('Guanajuato','Guanajuato') ,('Guerrero','Guerrero') ,('Hidalgo','Hidalgo') ,('Jalisco','Jalisco') ,('Michoacán','Michoacán') ,('Morelos','Morelos') ,('Nayarit','Nayarit') ,('Nuevo León','Nuevo León') ,('Oaxaca','Oaxaca') ,('Puebla','Puebla') ,('Querétaro','Querétaro') ,('Quintana Roo','Quintana Roo') ,('San Luis Potosí','San Luis Potosí') ,('Sinaloa','Sinaloa') ,('Sonora','Sonora') ,('Tabasco','Tabasco') ,('Tamaulipas','Tamaulipas') ,('Tlaxcala','Tlaxcala') ,('Veracruz','Veracruz') ,('Yucatán','Yucatán') ,('Zacatecas','Zacatecas')], string = "Estado",track_visibility='onchange')
    codPostal    = fields.Integer(string="C.P.",track_visibility='onchange')

    #Valores para impresión de factura
    valoresImpresion   = fields.One2many('servicios.valores', 'servicio',track_visibility='onchange')

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
    campo       = fields.Char(string = "Campo", track_visibility='onchange')
    valor       = fields.Char(string = "Valor", track_visibility="onchange")
    selection   = fields.Boolean(string="Select", default=False)