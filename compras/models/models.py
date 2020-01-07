# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from io import BytesIO
from PyPDF2 import PdfFileReader
from pdf2image import convert_from_path, convert_from_bytes
import os
import re

class compras(models.Model):
    _inherit = 'purchase.order'
    archivo=fields.Binary(store=True,readonly=False)
    nam=fields.Char(compute='_value_pc')
    
    
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
    @api.depends('archivo')
    def _value_pc(self):
        for record in self:
            record.order_line=[(5,0,0)]
            buf=""
            if(record.archivo!=False and type(record.archivo)!=type(None)):
                f2=base64.b64decode(record.archivo)
                try:
                    if f2.startswith(b'%PDF-1.4'):
                        with open(os.path.expanduser('test2.pdf'), 'wb') as fout:
                             fout.write(f2)
                        myCmd = 'pdftotext -fixed 5 test2.pdf test3.txt'
                        os.system(myCmd)
                        f = open("test3.txt","r")
                        string = f.read()
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
                               product={'product_id':productid.id,'product_qty':qty,'price_unit':g}
                               arr.append(product)
                        record['order_line']=arr
                except Exception:
                    print('hola')
                    #fin
                if f2.startswith(b'%PDF-1.7'):
                    with open(os.path.expanduser('test2.pdf'), 'wb') as fout:
                         fout.write(f2)
                    myCmd = 'pdftotext -fixed 5 test2.pdf test2.txt'
                    os.system(myCmd)
                    f = open("test2.txt","r")
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
                            product={'product_id':productid.id,'product_qty':cantidad,'price_unit':precio,'taxes_id':[10]}
                    record['order_line']=arreglo
                    
                else:
                    print('hola')

class comprasLine(models.Model):
    _inherit = 'purchase.order.line'
    serial=fields.Char()
