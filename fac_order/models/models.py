# -*- coding: utf-8 -*-

#from odoo import models, fields, api
from odoo import _, models, fields, api, tools
from email.utils import formataddr
from odoo.exceptions import UserError
from odoo import exceptions, _
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)

class fac_order(models.Model):
      _inherit = 'sale.order'
#     _name = 'fac_order.fac_order'

      nameDos = fields.Char()
      
     @api.multi 
     def llamado_boton(self):
         raise exceptions.Warning('No se pudo actualizar la dirreción de la solicitud: ')
