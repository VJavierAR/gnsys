from odoo import _,fields, api,models
from odoo.models import TransientModel
import datetime, time
from odoo.exceptions import UserError,RedirectWarning
from odoo.tools.float_utils import float_compare
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
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


class PurchaseAssig(models.Model):
	_name='purchase.assigned'
	_description='purchase assig'
	area=fields.Char('Area')
	solicitante=fields.Char('Solicitante')
	autoriza=fields.Char('Autoriza')

	def _default_purchase_ids(self):
		return self.env['purchase.order'].browse(self.env.context.get('active_ids'))
	purchase_ids=fields.Many2many('purchase.order',default=lambda self: self._default_purchase_ids(),)
	
	def confirmar(self):
		p=self.purchase_ids.write({'x_studio_autoriza':self.autoriza,'x_studio_area_de_solicitud':self.area,'x_studio_solicita':self.solicitante})
		return self.env.ref('studio_customization.studio_report_docume_0793fc55-e2af-4d93-a7cf-9ae38923bd11').report_action(p)
