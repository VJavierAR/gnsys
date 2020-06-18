# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
#from io import BytesIO
from pdf2image import convert_from_path, convert_from_bytes
import os
import re
from PyPDF2 import PdfFileMerger, PdfFileReader,PdfFileWriter
from io import BytesIO as StringIO
import base64
import datetime,time
from odoo.tools.mimetypes import guess_mimetype
import logging, ast
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
_logger = logging.getLogger(__name__)
import xml.etree.ElementTree as ET
from xml.dom import minidom


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



class compras(models.Model):
    _inherit = 'purchase.order'
    archivo=fields.Binary(store=True,readonly=False)
    nam=fields.Char()
    
    
    # @api.multi
    # def button_confirm(self):
    #     for order in self:
    #         if order.state not in ['draft', 'sent']:
    #             continue
    #         order._add_supplier_to_product()
    #         # Deal with double validation process
    #         if order.company_id.po_double_validation == 'one_step'\
    #                 or (order.company_id.po_double_validation == 'two_step'\
    #                     and order.amount_total < self.env.user.company_id.currency_id._convert(
    #                         order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
    #                 or order.user_has_groups('studio_customization.compras_aa157cfb-bb8b-4fcd-85da-04451cb98845'):
    #             order.button_approve()
    #         else:
    #             order.write({'state': 'to approve'})
    #     return True

    def solicitarAutorizacion(self):
        self.write({'state':'to approve'})
    
    @api.multi
    @api.onchange('archivo')
    def factura(self):
        if(self.archivo):
            f2=base64.b64decode(self.archivo)
            H=StringIO(f2)
            mimetype = guess_mimetype(f2 or b'')
            if(self.partner_id):
                #_logger.info(str(tree.getroot()))
                if(mimetype=='image/svg+xml' or mimetype=='application/octet-stream'):
                    tree = minidom.parse(H)
                    importe=0
                    arreglo=[]
                    total=tree.getElementsByTagName("cfdi:Comprobante")[0].getAttribute("Total")
                    con=tree.getElementsByTagName("cfdi:Concepto")
                    imp=tree.getElementsByTagName("cfdi:Traslado")
                    i=len(imp)
                    for c in con:
                        noparte=str(c.getAttribute("NoIdentificacion"))                
                        cantidad=float(c.getAttribute("Cantidad"))
                        precio=float(c.getAttribute("Importe"))
                        description=c.getAttribute("Descripcion")
                        product={'product_uom':1,'date_planned':self.date_order,'product_qty':cantidad,'price_unit':precio,'taxes_id':[10]}
                        descuento=float(c.getAttribute("Descuento")) if(c.getAttribute("Descuento")!='') else 0
                        precioCdesc=(round(precio,6)-round(descuento,6))/int(cantidad)
                        #_logger.info(noparte=='')
                        if(noparte!=''):
                            template=self.env['product.template'].search([('default_code','=',noparte.split('0',1)[1] if(noparte[0]=="0") else noparte)])
                            if(template.id==False):
                                template=self.env['product.template'].create({'name':'','description':description,'categ_id':self.x_studio_tipo_de_producto.id,'default_code':noparte})
                            productid=self.env['product.product'].search([('product_tmpl_id','=',template.id)])
                            product['product_id']=productid.id
                            product['name']=description
                            product['price_unit']=precioCdesc
                            product['price_subtotal']=precio-descuento
                        if(noparte==''):
                            product['product_id']=11027
                            product['product_uom']=21
                            product['name']=description
                            product['price_unit']=precioCdesc
                            product['price_subtotal']=precio-descuento
                        arreglo.append(product) 
                    if(len(arreglo)>0):
                       self.order_line=[(5,0,0)]
                       self.order_line=arreglo
                    #time.sleep(30)
                    _logger.info(str(float(imp[i-1].getAttribute("Importe"))))
                    self.x_studio_impuesto=float(imp[i-1].getAttribute("Importe"))
                    self.x_studio_total=float(total)
                if(mimetype=='application/pdf'):
                    self.x_studio_pdf=self.archivo
                    myCmd = 'pdftotext -fixed 5 hola.pdf test3.txt'
                    if(self.archivo and ("katun" in self.partner_id.name.lower())):
                        myCmd = 'pdftotext -fixed 3 hola.pdf test3.txt'
                        out = open("hola.pdf", "wb")
                        #f2=base64.b64decode(self.archivo)
                        #H=StringIO(f2)
                        file = PdfFileReader(H)
                        t=PdfFileWriter()
                        for p in range(file.getNumPages()):
                            t.addPage(file.getPage(p))
                        t.write(out)
                        out.close()
                        os.system(myCmd)
                        f = open("test3.txt","r")
                        string = f.read()
                        f.close()
                        arr=string.split('\n')
                        arreglo=[]
                        for ar in arr:
                            if('Pieza' in ar):
                                cantidad=float(ar.split('      ',1)[1].split('        ',1)[0].replace(' ',''))
                                _logger.info(str(str(ar.split(' '+str(int(cantidad))+' '))[2].split(' ')))
                                noparte=ar.split('      ',1)[1].split('        ',1)[1].split('            ',1)[0].split(str(ar.split('      ',1)[1].split('        ',1)[0].replace(' ','')),1)[1]
                                _logger.info(str(noparte))
                                p=ar.split('$')
                                precio=float(p[1].replace(' ',''))
                                descuento=float(p[4].replace(' ','')) if(len(p)==5) else 0
                                precioCdesc=((cantidad*precio)-descuento)/cantidad
                                template=self.env['product.template'].search([('default_code','=',noparte.replace(' ',''))])
                                if(template.id==False):
                                    template=self.env['product.template'].create({'name':'','description':'/','categ_id':self.x_studio_tipo_de_producto.id,'default_code':noparte})
                                productid=self.env['product.product'].search([('product_tmpl_id','=',template.id)])
                                product={'product_uom':1,'date_planned':self.date_order,'product_id':productid.id,'product_qty':cantidad,'price_unit':precioCdesc,'taxes_id':[10],'name':productid.description if(productid.description) else '/'}
                                arreglo.append(product)
                            if('E48' in ar):
                                p=ar.split('$')
                                product={'product_uom':1,'date_planned':self.date_order,'product_id':1,'product_qty':1,'price_unit':float(p[1].replace(' ','')),'taxes_id':[10],'name':productid.description if(productid.description) else '/'}
                                arreglo.append(product)
                        if(len(arreglo)>0):
                            self.order_line=[(5,0,0)]
                        self.order_line=arreglo
                    if(self.archivo and ("ctr" in self.partner_id.name.lower())):
                        myCmd = 'pdftotext -fixed 4 hola.pdf test3.txt'
                        out = open("hola.pdf", "wb")
                        #f2=base64.b64decode(self.archivo)
                        #H=StringIO(f2)
                        file = PdfFileReader(H)
                        t=PdfFileWriter()
                        for p in range(file.getNumPages()):
                            t.addPage(file.getPage(p))
                        t.write(out)
                        out.close()
                        os.system(myCmd)
                        f = open("test3.txt","r")
                        string = f.read()
                        f.close()
                        text=string.split('Importe')[1].split('\n')
                        fff=open("tt.txt","w")
                        arreglo=[]
                        for t in text:
                            if('H87 -' in t):
                                tt=t.split('H87 -')
                                cantidad=float(tt[0].replace(' ',''))
                                tt2=tt[1].split('$')
                                noparte=tt2[0].split('      ')[2].split('    ')[0].split('0',1)[1]
                                precio=float(tt2[1].replace(' ','').replace(',',''))
                                descuento=float(tt2[2].split('002-IVA')[0].replace(' ','').replace(',',''))
                                precioCdesc=((cantidad*precio)-descuento)/cantidad
                                template=self.env['product.template'].search([('default_code','=',noparte)])
                                if(template.id==False):
                                    template=self.env['product.template'].create({'name':'','description':'/','categ_id':self.x_studio_tipo_de_producto.id,'default_code':noparte})
                                productid=self.env['product.product'].search([('product_tmpl_id','=',template.id)])
                                product={'product_uom':1,'date_planned':self.date_order,'product_id':productid.id,'product_qty':cantidad,'price_unit':precioCdesc,'taxes_id':[10],'name':productid.description if(productid.description) else '/'}
                                fff.write(str(product)+str(noparte))
                                arreglo.append(product)
                        if(len(arreglo)>0):
                            self.order_line=[(5,0,0)]
                        self.order_line=arreglo
                        fff.close()
                    if(self.archivo and ("konica" in self.partner_id.name.lower() or "kyocera" in self.partner_id.name.lower())):
                        out = open("hola.pdf", "wb")
                        #f2=base64.b64decode(self.archivo)
                        #H=StringIO(f2)
                        file = PdfFileReader(H)
                        t=PdfFileWriter()
                        for p in range(file.getNumPages()):
                            t.addPage(file.getPage(p))
                        t.write(out)
                        out.close()
                        os.system(myCmd)
                        f = open("test3.txt","r")
                        if f2.startswith(b'%PDF-1.7'):
                            string = f.read()
                            f.close()
                            d = string.split('\n')
                            n=len(d)
                            arreglo=[]
                            product={}
                            i=0
                            for x in d:
                                f=x
                                serial=''
                                if ('PIEZA' in f):
                                    cantidad = f.split('PIEZA')[0]
                                    l = f.split('PIEZA')[1].split(' -',2)
                                    id = l[1].replace(' ','')
                                    casi = l[2].split('.')
                                    _logger.info(str(casi))
                                    casii = casi[1].split(' ')[0]
                                    tam = casi[0].split(' ')
                                    p = len(tam)
                                    m = tam[p-1]+'.'+casii
                                    precio = (float(m.replace(',',''))-(float(m.replace(',',''))*(self.x_studio_descuento/100)))
                                    template=self.env['product.template'].search([('default_code','=',id)])
                                    if(template.id==False):
                                        productid=self.env['product.product'].create({'name':casi[0],'description':casi[0],'categ_id':self.x_studio_tipo_de_producto.id,'default_code':str(id),'type':'product'})                                        
                                    if(template.id!=False):
                                        productid=self.env['product.product'].search([('product_tmpl_id','=',template.id)])
                                    _logger.info('id'+str(id))
                                    product={'product_uom':1,'date_planned':self.date_order if(self.date_order) else datetime.datetime.now()-datetime.timedelta(hours=-5),'product_id':productid.id,'product_qty':cantidad,'price_unit':precio,'taxes_id':[10],'name':productid.description}
                                    arreglo.append(product)
                            if(len(arreglo)>0):
                                self.order_line=[(5,0,0)]
                            self.order_line=arreglo
                        if f2.startswith(b'%PDF-1.4'):
                            string = f.read()
                            f.close()
                            b = string.split('\n')                    
                            i = 0
                            j=0
                            h=""
                            g=""
                            q=""
                            qty=""
                            arr=[]
                            for o in b:
                                product={}
                                if('#' in o ):
                                    r = o.split(" Artículo # ")
                                    q = r[1].split(' ')[0]
                                    _logger.info(str(r))
                                    template=self.env['product.template'].search([('default_code','=',q)])
                                    if(template.id==False):
                                        productid=self.env['product.product'].create({'name':'/','description':'falta','categ_id':self.x_studio_tipo_de_producto.id,'default_code':str(q),'type':'product'})
                                    if(template.id!=False):                                  
                                        productid=self.env['product.product'].search([('product_tmpl_id','=',template.id)])
                                    if(len(arr)==i+1):
                                        arr[i]['product_id']=productid.id
                                        desc=productid.description if(productid.description) else '|'
                                        arr[i]['name']=desc
                                        arr[i]['product_uom']=1
                                        arr[i]['date_planned']=self.date_order if(self.date_order) else datetime.datetime.now()-datetime.timedelta(hours=-5)
                                        arr[i]['taxes_id']=[10]
                                    if(len(arr)==i):
                                        product={'product_uom':1,'date_planned':self.date_order if(self.date_order) else datetime.datetime.now()-datetime.timedelta(hours=-5),'product_id':productid.id,'taxes_id':[10],'name':productid.description}
                                        desc=productid.description if(productid.description) else '|'
                                        product['name']=desc
                                        arr.append(product)
                                    i=i+1       
                                if('Customer' in o or 'SUPPLY' in o):
                                    s = o.split("$")
                                    h=float(s[2])
                                    g=float(s[1].split(' ')[0])
                                    qty=round(h/g)
                                    if(len(arr)==j+1):
                                        arr[j]['product_qty']=qty
                                        arr[j]['price_unit']=g/1.16
                                    if(len(arr)==j):
                                        product={'product_qty':qty,'price_unit':g/1.16}
                                        arr.append(product)
                                    j=j+1
                            if(len(arr)>0):
                                self.order_line=[(5,0,0)]
                            self.order_line=arr
                if(mimetype=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
                    book = xlrd.open_workbook(file_contents=f2 or b'')
                    sheet = book.sheet_by_index(0)
                    header=[]
                    arr=[]
                    descuento=self.x_studio_descuento/100 if(self.x_studio_descuento!=False) else 0
                    for row_num, row in enumerate(sheet.get_rows()):
                        #_logger.info()
                        #_logger.info(str(self.partner_id.name))
                        #_logger.info(str(row[0].value))


                        if(row[0].value in self.partner_id.name.replace(' ','') and str(row[0].ctype)!='0'):
                            product={}
                            producto=row[2].value
                            precio=float(row[10].value)
                            #_logger.info(row[10].value)
                            cantidad=int(row[8].value) if(row[8].ctype!=0) else 0
                            #_logger.info(str(producto).replace(' ',''))
                            template=self.env['product.template'].search([('default_code','=',str(producto).replace('.0',''))])
                            if(template.id==False):
                                template=self.env['product.template'].create({'name':'','description':'/','categ_id':self.x_studio_tipo_de_producto.id,'default_code':str(producto).replace('.0','')})
                            productid=self.env['product.product'].search([('product_tmpl_id','=',template.id)])
                            product={'product_uom':1,'date_planned':self.date_order,'product_id':productid.id,'product_qty':cantidad,'price_unit':precio,'name':productid.description}
                            product['taxes_id']=[10]
                            if("KATUN" in row[0].value):
                                product['price_unit']=float(row[10].value)-float(row[10].value)*descuento
                                product['taxes_id']=[10]
                            if("CTR" in row[0].value):
                                #descuento=float(row[15].value) if(row[15].ctype!=0) else 0
                                product['price_unit']=float(row[10].value)-(float(row[10].value)*descuento)
                                product['taxes_id']=[10]
                            arr.append(product)
                    if(len(arr)>0):
                        self.order_line=[(5,0,0)]
                    self.order_line=arr
                            #header.append(str(row))
                        #for cell in row:
                        #  print(row)  # Print out the header
                            #if(cell.value!=None or cell.value!=''):
                                
                        # emulate Sheet.get_rows for pre-0.9.4
                        #for row in pycompat.imap(sheet.row, range(sheet.nrows)):
                        #    values = []
                    #    for cell in row:
                    #_logger.info(str(header))
                    _logger.info(str(arr))

    def registrarPago(self):
        _logger.info(str(len(self.invoice_ids)))
        if(len(self.x_studio_field_H9kGQ)==0):
            result = {
            'type': 'in_invoice',
            'purchase_id': self.id,
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
            'partner_id':self.partner_id.id,
            'origin':self.name}
            p=self.env['account.invoice'].create(result)
            #lines=self.env['account.invoice.line']
            p._onchange_bill_purchase_order()
            p._onchange_allowed_purchase_ids()
            #for line in self.order_line:
            #    p._prepare_invoice_line_from_po_line(line)
            #p._onchange_product_id()
            p.purchase_order_change()
            p._onchange_currency_id()
            p._onchange_partner_id()
            p.compute_taxes()
            p.write({'purchase_id':self.id})
        if(len(self.x_studio_field_H9kGQ)==1):
            self.action_view_invoice()
        if(len(self.x_studio_field_H9kGQ)>1):
            self.action_view_invoice()

class comprasLine(models.Model):
    _inherit = 'purchase.order.line'
    serial=fields.Char()

class GastosGnsysVC(models.Model):    
    _name='gastos.gnsys.vc' 
    _description='Modulo de Gastos V.C' 
    solicitante=fields.Many2one('hr.employee','Solicitante')    
    rubro=fields.Selection([["GASTOS TRANSPORTE","GASTOS TRANSPORTE"], ["GASTOS DE OPERACION","GASTOS DE OPERACION"], ["SERVICIOS GENERALES ","SERVICIOS GENERALES "], ["INSUMOS PARA OFICINA ","INSUMOS PARA OFICINA "], ["EQUIPO DE TRANSPORTE ","EQUIPO DE TRANSPORTE "], ["SERVICIOS DE PERSONAL ","SERVICIOS DE PERSONAL "], ["ARRENDAMIENTO DE INMUEBLES ","ARRENDAMIENTO DE INMUEBLES "], ["EQUIPO DE TRANSPORTE","EQUIPO DE TRANSPORTE"], ["SERVICIOS PROFESIONALES","SERVICIOS PROFESIONALES"], ["INSUMOS PARA SERVICIO","INSUMOS PARA SERVICIO"], ["EXTRAORDINARIOS ","EXTRAORDINARIOS "], ["EXTRAORDINARIOS","EXTRAORDINARIOS"], ["IMPUESTOS SAT","IMPUESTOS SAT"], ["MOBILIARIO Y EQUIPO","MOBILIARIO Y EQUIPO"], ["SERVICIOS PROFESIONALES ","SERVICIOS PROFESIONALES "], ["INSUMOS PARA OFICINA","INSUMOS PARA OFICINA"], ["SERVICIOS DE PERSONAL","SERVICIOS DE PERSONAL"]]) 
    concepto=fields.Char('Concepto')    
    aplicacion=fields.Many2one('x_aplicacion','Aplicacion') 
    monto=fields.Float('Monto',widget='monetary')
