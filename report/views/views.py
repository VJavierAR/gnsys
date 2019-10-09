# -*- coding: utf-8 -*-

from odoo import models, fields, api




class report(models.AbstractModel):
    _name = 'report.report_custom_template'
    
    def _get_picking(self):
        ordenes=self.env['stock.picking'].browse(self.env.context.get('active_ids'))
        return ordenes
    
    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('module.report_name')
        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self._get_picking(),
        }
        return report_obj.render('module.report_name', docargs)
