# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging, ast
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
_logger = logging.getLogger(__name__)

class SaleOrderCompatibles(http.Controller):
    @http.route('/tfs/autoriza/<int:tfs_id>', auth='public')
    def index(self, tfs_id,**kw):
        p=request.env['tfs.tfs'].search([['id','=',tfs_id]])
        p.valida()   
        return "Proceso  "+str(p.name)+" Autorizado"


class SaleOrderCompatiblesCancel(http.Controller):
    @http.route('/tfs/cancela/<int:tfs_id>', auth='public')
    def index(self, tfs_id,**kw):
        p=request.env['tfs.tfs'].search([['id','=',tfs_id]])
        p.canc()
        return "Proceso  "+str(p.name)+" Cancelado"