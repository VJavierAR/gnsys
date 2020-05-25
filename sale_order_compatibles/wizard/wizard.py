
"""
from odoo import fields, api
from odoo.models import TransientModel
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from odoo import exceptions, _

class SaleMailMessage(TransientModel):
    _name = 'sale.mail.message'
    _description = 'Sale order Message'
"""