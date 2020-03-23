from odoo import models
import logging, ast
_logger = logging.getLogger(__name__)



class PartnerXlsx(models.AbstractModel):
    _name = 'report.module_name.report_name'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        #for obj in partners:
        #    report_name = obj.name
            # One sheet by partner
        sheet = workbook.add_worksheet("clientes")
        #    bold = workbook.add_format({'bold': True})
        #    sheet.write(0, 0, obj.name, bold)
        _logger.info("HOLAAAAAAAAAAAAAAAAA")