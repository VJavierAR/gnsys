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
        myCmd = 'pdftotext -fixed 5 hola.pdf test3.txt'
        if(self.archivo and "konica" in self.partner_id.name.lower()):
            out = open("hola.pdf", "wb")
            f2=base64.b64decode(self.archivo)
            H=StringIO(f2)
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
                        product={'product_uom':1,'date_planned':self.date_order,'product_id':productid.id,'product_qty':cantidad,'price_unit':precio,'taxes_id':[10],'name':' '}
                self.order_line=arreglo
            
            
class comprasLine(models.Model):
    _inherit = 'purchase.order.line'
    serial=fields.Char()
