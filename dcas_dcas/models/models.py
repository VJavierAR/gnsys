# -*- coding: utf-8 -*-

from odoo import models, fields, api

 class dcas_dcas(models.Model):
     _name = 'dcas_update'
     _inherit = 'dcas.dcas'

     active = fields.Boolean(string = 'Active', default = True)


     