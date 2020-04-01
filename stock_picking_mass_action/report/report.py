from odoo import models
import logging, ast
import datetime, time
import xlsxwriter
_logger = logging.getLogger(__name__)

class PartnerXlsx(models.AbstractModel):
    _name = 'report.requisicion.partner_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        i=2
        d=[]
        partners=self.env['stock.move.line'].browse(eval(partners.x_studio_arreglo))
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'blue'})
        report_name = 'Movimientos'
        bold = workbook.add_format({'bold': True})
        sheet = workbook.add_worksheet('Movimientos')
        sheet.merge_range('A1:K1', 'Movimientos de Almacen', merge_format)
        #header1 = '&CHere is some centered text.'
        #sheet.set_header('A1', {'image_left': '/home/odoo/logo.png'})
        #image_file = open('/home/odoo/logo.png', 'rb')
        #image_data = xlsxwriter.compatibility.BytesIO(image_file.read())
        #sheet.set_header('&C', {'image_center': image_data})
        #sheet.insert_image('A1', 'logo.png')
        for obj in partners:
            e=[]
            #e.append(obj.name)
            #e.append(obj.street)
            d.append(e)
            # One sheet by partner
            
            #_logger.info('work')
            sheet.write(i, 0, obj.x_studio_field_aVMhn.name, bold)
            sheet.write(i, 1, obj.date.strftime("%Y/%m/%d"), bold)
            sheet.write(i, 2, obj.x_studio_field_3lDS0.name, bold)
            if(obj.location_id.id==obj.x_studio_field_3lDS0.wh_input_stock_loc_id.id):
                sheet.write(i, 3, "Entrada", bold)
            if(obj.location_id.id!=obj.x_studio_field_3lDS0.wh_input_stock_loc_id.id):
                sheet.write(i, 3, "Salida", bold)
            sheet.write(i, 4, obj.product_id.name, bold)
            sheet.write(i, 5, obj.product_id.default_code, bold)
            sheet.write(i, 6, obj.qty_done, bold)
            if(obj.lot_id):
                sheet.write(i, 7, obj.lot_id.name, bold)
            if(obj.lot_id==False):
                sheet.write(i, 7, obj.move_id.x_studio_serieorderline, bold)
            sheet.write(i, 8, obj.move_id.picking_id.partner_id.parent_id.name, bold)
            sheet.write(i, 9, obj.move_id.picking_id.partner_id.name, bold)
            sheet.write(i, 10, obj.move_id.picking_id.x_studio_comentario_1, bold)
            if(obj.x_studio_ticket):
                sheet.write(i,11, obj.x_studio_ticket, bold)
            if(obj.x_studio_ticket==False):
                sheet.write(i, 11, obj.x_studio_ticket, bold) 
            sheet.write(i, 12, obj.move_id.picking_id.partner_id.city, bold)            
            sheet.write(i, 13, obj.move_id.picking_id.partner_id.state_id.name, bold)
            user=self.env['stock.picking'].search(['&',['sale_id','=',obj.picking_id.sale_id.id],['location_id','=',obj.x_studio_field_3lDS0.lot_stock_id.id]])
            sheet.write(i, 14, user.write_uid.name, bold)

            i=i+1
        sheet.add_table('A2:O'+str((i)),{'style': 'Table Style Medium 9','columns': [{'header': 'Categoria'},{'header': 'Fecha'},{'header': 'Almacen'},{'header':'Tipo'},{'header': 'Modelo'},{'header': 'No Parte'},{'header': 'Cantidad'},{'header': 'Serie'},{'header': 'Cliente'},{'header': 'Localidad'},{'header': 'Comentario'},{'header': 'Documento Origen'},{'header': 'Estado'},{'header': 'Delegación'},{'header': 'Usuario'}]})
        workbook.close()