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

class comprasLine(models.Model):
    _inherit = 'purchase.order.line'
    serial=fields.Char()
