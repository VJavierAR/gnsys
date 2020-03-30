from odoo import models
import logging, ast
import datetime, time
import xlsxwriter
_logger = logging.getLogger(__name__)

class PartnerXlsx(models.AbstractModel):
    _name = 'report.requisicion.partner_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        i=1
        d=[]
        report_name = 'Clientes'
        bold = workbook.add_format({'bold': True})
        sheet = workbook.add_worksheet('Clientes')
        #sheet.set_header('A1', {'image_left': 'logo.png'})
        #sheet.write(0, 0, 'Cliente', bold)
        #sheet.insert_image('A1', 'logo.png')
        for obj in partners:
            e=[]
            e.append(obj.name)
            e.append(obj.street)
            d.append(e)
            # One sheet by partner
            
            #_logger.info('work')
            sheet.write(i, 0, obj.name, bold)
            sheet.write(i, 1, obj.street, bold)
            i=i+1
        sheet.add_table('A1:B'+str((i+1)),{'columns': [{'header': 'Cliente'},{'header': 'Calle'}]})
        workbook.close()