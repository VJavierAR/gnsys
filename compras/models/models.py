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
import datetime
from odoo.tools.mimetypes import guess_mimetype
import logging, ast
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
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



class compras(models.Model):
    _inherit = 'purchase.order'
    archivo=fields.Binary(store=True,readonly=False)
    nam=fields.Char()
    
    
    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.user.company_id.currency_id._convert(
                            order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
                    or order.user_has_groups('studio_customization.compras_aa157cfb-bb8b-4fcd-85da-04451cb98845'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True

    
    
    
    @api.multi
    @api.onchange('archivo')
    def factura(self):
        if(self.archivo):
            f2=base64.b64decode(self.archivo)
            H=StringIO(f2)
            mimetype = guess_mimetype(f2 or b'')
            if(self.partner_id):
                if(mimetype=='application/pdf'):
                    myCmd = 'pdftotext -fixed 5 hola.pdf test3.txt'
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
                            producto={}
                            for x in d:
                                f=x
                                serial=''
                                if(len(re.findall(r"\d{2}\/\d{2}\/\d{4}\s*", f))>0):
                                    serial=f.split('-')[0].replace(' ','')
                                    product['serial']=serial
                                    arreglo.append(product)
                                if ('PIEZA' in f):
                                    cantidad = f.split('PIEZA')[0]
                                    l = f.split('PIEZA')[1].split(' -',1)
                                    #id = l[0]
                                    id = l[0].split('    ')[1]
                                    casi = l[1].split('.')
                                    casii = casi[1].split(' ')[0]
                                    tam = casi[0].split(' ')
                                    p = len(tam)
                                    m = tam[p-1]+'.'+casii
                                    precio = m.replace(',','')
                                    template=self.env['product.template'].search([('default_code','=',id)])
                                    productid=self.env['product.product'].search([('product_tmpl_id','=',template.id)])
                                    product={'product_uom':1,'date_planned':self.date_order,'product_id':productid.id,'product_qty':cantidad,'price_unit':precio,'taxes_id':[10],'name':productid.description}
                            if(len(arreglo)>0):
                                self.order_line=[(5,0,0)]
                            self.order_line=arreglo
                        if f2.startswith(b'%PDF-1.4'):
                            string = f.read()
                            f.close()
                            b = re.split('\n',string)                    
                            i = 0
                            h=""
                            g=""
                            q=""
                            qty=""
                            arr=[]
                            for o in b:
                                if('#' in o ):
                                   r = o.split("#")
                                   q = r[1].split(' ')[1]       
                                if('Customer Pick' in o ):
                                   s = o.split("$")
                                   h=float(s[2])
                                   g=float(s[1].split(' ')[0])
                                   qty=round(h/g)
                                   template=self.env['product.template'].search([('default_code','=',q)])
                                   productid=self.env['product.product'].search([('product_tmpl_id','=',template.id)])
                                   product={'product_uom':1,'date_planned':self.date_order,'product_id':productid.id,'product_qty':qty,'price_unit':g,'name':productid.description}
                                   arr.append(product)
                            if(len(arr)>0):
                                self.order_line=[(5,0,0)]
                            self.order_line=arr
                if(mimetype=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
                    book = xlrd.open_workbook(file_contents=f2 or b'')
                    sheet = book.sheet_by_index(0)
                    header=[]
                    for row_num, row in enumerate(sheet.get_rows()):
                        _logger.info(str(row[0].value))

                        if(row[0].value in self.partner_id.name):
                            header.append(str(row))
                        #for cell in row:
                        #  print(row)  # Print out the header
                            #if(cell.value!=None or cell.value!=''):
                                
                        # emulate Sheet.get_rows for pre-0.9.4
                        #for row in pycompat.imap(sheet.row, range(sheet.nrows)):
                        #    values = []
                    #    for cell in row:
                    _logger.info(str(header))


            
class comprasLine(models.Model):
    _inherit = 'purchase.order.line'
    serial=fields.Char()
