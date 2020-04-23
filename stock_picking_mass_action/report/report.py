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
        if(len(partners)==1 and partners.x_studio_arreglo!='/' and partners.x_studio_arreglo!=False):
            copia=partners
            partners=self.env['stock.move.line'].browse(eval(partners.x_studio_arreglo))
            copia.write({'x_studio_arreglo':'/'})
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'blue'})
        report_name = 'Movimientos'
        bold = workbook.add_format({'bold': True})
        sheet = workbook.add_worksheet('Movimientos')
        sheet.merge_range('A1:Q1', 'Movimientos de Almacen', merge_format)
        #header1 = '&CHere is some centered text.'
        #sheet.set_header('A1', {'image_left': '/home/odoo/logo.png'})
        #image_file = open('/home/odoo/logo.png', 'rb')
        #image_data = xlsxwriter.compatibility.BytesIO(image_file.read())
        #sheet.set_header('&C', {'image_center': image_data})
        #sheet.insert_image('A1', 'logo.png')
        for obj in partners:
            e=[]
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
            if(obj.lot_id==False):
                sheet.write(i, 7, obj.product_id.default_code, bold)
            sheet.write(i, 8, obj.x_studio_cliente_1 if(obj.x_studio_cliente_1) else '', bold)
            sheet.write(i, 9, obj.x_studio_localidad if(obj..x_studio_localidad) else '', bold)
            sheet.write(i, 10, obj.move_id.picking_id.x_studio_comentario_1 if(obj.move_id.picking_id.x_studio_comentario_1) else '', bold)
            if(obj.x_studio_ticket):
                sheet.write(i,11, obj.x_studio_ticket, bold)
            if(obj.x_studio_ticket==False):
                sheet.write(i, 11, obj.x_studio_ticket, bold)
            sheet.write(i, 12, obj.x_studio_serie_destino_1 if(obj.x_studio_serie_destino_1) else '', bold)            
            sheet.write(i, 13, obj.x_studio_modelo_equipo if(obj.x_studio_modelo_equipo) else '', bold)                 
            sheet.write(i, 14, obj.move_id.picking_id.partner_id.city if(obj.move_id.picking_id.partner_id.city) else '', bold)            
            sheet.write(i, 15, obj.move_id.picking_id.partner_id.state_id.name if(obj.move_id.picking_id.partner_id.state_id.name) else '', bold)
            user=self.env['stock.picking'].search(['&',['sale_id','=',obj.picking_id.sale_id.id],['location_id','=',obj.x_studio_field_3lDS0.lot_stock_id.id]])
            if(len(user)>1):
                sheet.write(i, 16, user[0].write_uid.name if(user[0].write_uid.name) else '', bold)
            if(len(user)<=1):
                sheet.write(i, 16, user.write_uid.name if(user.write_uid.name) else '', bold)

            i=i+1
        sheet.add_table('A2:Q'+str((i)),{'style': 'Table Style Medium 9','columns': [{'header': 'Categoria'},{'header': 'Fecha'},{'header': 'Almacen'},{'header':'Tipo'},{'header': 'Modelo'},{'header': 'No Parte'},{'header': 'Cantidad'},{'header': 'Serie'},{'header': 'Cliente'},{'header': 'Localidad'},{'header': 'Comentario'},{'header': 'Documento Origen'},{'header': 'Serie Destino'},{'header': 'Modelo Destino'},{'header': 'Estado'},{'header': 'Delegación'},{'header': 'Usuario'}]})
        workbook.close()

class ExistenciasXML(models.AbstractModel):
    _name = 'report.existencias.report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, quants):
        if(len(quants)==1 and quants.x_studio_arreglo!='/' and quants.x_studio_arreglo!=False):
            copia=quants
            quants=self.env['stock.quant'].browse(eval(quants.x_studio_arreglo))
            copia.write({'x_studio_arreglo':'/'})
        t=quants[0].lot_id.id
        i=2
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'blue'})
        report_name = 'Existencias'
        bold = workbook.add_format({'bold': True})
        if(t):
            sheet = workbook.add_worksheet('Existencias Equipos')
            sheet.merge_range('A1:H1', 'Existencias Equipos', merge_format)   
            for obj in quants:
                sheet.write(i, 0, obj.x_studio_almacn.name, bold)
                sheet.write(i, 1, obj.product_id.name, bold)
                sheet.write(i, 2, obj.product_id.default_code, bold)
                sheet.write(i, 3, obj.product_id.description, bold)
                sheet.write(i, 4, obj.lot_id.name, bold)
                sheet.write(i, 5, obj.lot_id.x_studio_estado, bold)
                sheet.write(i, 6, obj.reserved_quantity, bold)
                sheet.write(i, 7, obj.x_studio_field_kUc4x.x_name, bold)
                i=i+1
            sheet.add_table('A2:H'+str((i)),{'style': 'Table Style Medium 9','columns': [{'header': 'Almacen'},{'header': 'Modelo'},{'header': 'No Parte'},{'header':'Descripción'},{'header':'No Serie'},{'header': 'Estado'},{'header': 'Apartados'},{'header': 'Ubicación'}]}) 
        else:
            sheet = workbook.add_worksheet('Existencias Componentes')
            sheet.merge_range('A1:G1', 'Existencias Componentes', merge_format)   
            for obj in quants:
                sheet.write(i, 0, obj.x_studio_almacn.name, bold)
                sheet.write(i, 1, obj.product_id.name, bold)
                sheet.write(i, 2, obj.product_id.default_code, bold)
                sheet.write(i, 3, obj.product_id.description, bold)
                sheet.write(i, 4, obj.quantity, bold)
                sheet.write(i, 5, obj.reserved_quantity, bold)
                sheet.write(i, 6, obj.x_studio_field_kUc4x.x_name, bold)
                i=i+1
            sheet.add_table('A2:G'+str((i)),{'style': 'Table Style Medium 9','columns': [{'header': 'Almacen'},{'header': 'Modelo'},{'header': 'No Parte'},{'header':'Descripción'},{'header': 'Existencia'},{'header': 'Apartados'},{'header': 'Ubicación'}]}) 
        workbook.close()


class PartnerXlsx(models.AbstractModel):
    _name = 'report.solicitudes.report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, sale):
        i=2
        d=[]
        if(len(sale)==1 and sale.x_studio_arreglo!='/' and sale.x_studio_arreglo!=False):
            copia=sale
            sale=self.env['sale.order'].browse(eval(sale.x_studio_arreglo)).sorted(key='write_date',reverse=True) 
            copia.write({'x_studio_arreglo':'/'})
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'blue'})
        report_name = 'Solicitudes'
        bold = workbook.add_format({'bold': True})
        sheet = workbook.add_worksheet('Solicitudes')
        sheet.merge_range('A1:Q1', 'Solicitudes', merge_format)
        for obj in sale:
                sheet.write(i, 0, obj.name, bold)
                sheet.write(i, 1, obj.write_date.strftime("%Y/%m/%d"), bold)
                sheet.write(i, 2, obj.partner_id.name, bold)
                sheet.write(i, 3, obj.partner_shipping_id.name, bold)
                sheet.write(i, 4, obj.warehouse_id.name, bold)
                sheet.write(i, 5, obj.x_studio_status, bold)
                sheet.write(i, 6, str(obj.order_line.filtered(lambda x:x.product_id.categ_id.id==13).mapped('product_id.name')), bold)
                sheet.write(i, 7, str(self.env['stock.move.line'].search([['picking_id.sale_id','=',obj.id],['lot_id','!=',False]]).mapped('lot_id.name')), bold)
                sheet.write(i, 8, str(obj.order_line.filtered(lambda x:x.product_id.categ_id.id==11).mapped('product_id.name')), bold)
                sheet.write(i, 9, str(obj.order_line.filtered(lambda x:x.product_id.categ_id.id==5).mapped('product_id.name')), bold)
                sheet.write(i, 10, len(obj.order_line.filtered(lambda x:x.product_id.categ_id.id==13).mapped('product_id.name')), bold)
                sheet.write(i, 11, len(obj.order_line.filtered(lambda x:x.product_id.categ_id.id!=13).mapped('product_id.name')), bold)
                sheet.write(i, 12, obj.x_studio_tipo_de_solicitud, bold)
                sheet.write(i, 13, str(str(obj.state)+'/'+obj.write_uid.name), bold)
                sheet.write(i, 14, obj.create_uid.name, bold)
                sheet.write(i, 15, 'Asignado' if(obj.user_id) else 'No Asignado', bold)
                sheet.write(i, 16, str(obj.note), bold)
                i=i+1
        sheet.add_table('A2:Q'+str(i),{'style': 'Table Style Medium 9','columns': [{'header': 'Numero de solicitud'},{'header': 'Fecha'},{'header': 'Cliente'},{'header':'Localidades'},{'header': 'Almacen'},{'header': 'Estado'},{'header': 'Modelo'},{'header': 'No. De serie'},{'header': 'Accesorio'},{'header': 'Toner'},{'header': 'Número de equipos'},{'header': 'Número de componentes'},{'header': 'Tipo'},{'header': 'Status'},{'header': 'Usuario Creación'},{'header': 'Asignado'},{'header': 'Comentarios'}]}) 
        workbook.close()

class PartnerXlsx(models.AbstractModel):
    _name = 'report.tickets.report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, ticket):
        i=2
        d=[]
        if(len(ticket)==1 and ticket.x_studio_arreglo!='/' and ticket.x_studio_arreglo!=False):
            copia=ticket
            ticket=self.env['helpdesk.ticket'].browse(eval(ticket.x_studio_arreglo)).sorted(key='create_date',reverse=True) 
            copia.write({'x_studio_arreglo':'/'})
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'blue'})
        report_name = 'Tickets'
        bold = workbook.add_format({'bold': True})
        sheet = workbook.add_worksheet('Tickets')
        sheet.merge_range('A1:Q1', 'Tickets', merge_format)
        for obj in ticket:
                sheet.write(i, 0, obj.name, bold)
                sheet.write(i, 1, obj.x_studio_tipo_de_vale if(obj.x_studio_tipo_de_vale) else '', bold)
                sheet.write(i, 2, obj.create_date.strftime("%Y/%m/%d"), bold)
                sheet.write(i, 3, obj.days_difference, bold)
                sheet.write(i, 4, obj.partner_id.name if(obj.partner_id) else '', bold)
                sheet.write(i, 5, obj.x_studio_empresas_relacionadas.name if(obj.x_studio_empresas_relacionadas) else '', bold)
                sheet.write(i, 6, str(obj.x_studio_equipo_por_nmero_de_serie_1.sorted(key='id').mapped('serie.name')) if(obj.team_id.id==8) else str(obj.x_studio_equipo_por_nmero_de_serie.sorted(key='id').mapped('name')), bold)
                sheet.write(i, 7, str(obj.x_studio_equipo_por_nmero_de_serie_1.sorted(key='id').mapped('serie.product_id.name')) if(obj.team_id.id==8) else str(obj.x_studio_equipo_por_nmero_de_serie.sorted(key='id').mapped('product_id.name')), bold)
                sheet.write(i, 8, obj.team_id.name, bold)
                sheet.write(i, 9,obj.x_studio_empresas_relacionadas.state_id.name if(obj.x_studio_empresas_relacionadas.state_id) else '' , bold)
                sheet.write(i, 10, obj.description if(obj.description) else '', bold)
                sheet.write(i, 11, obj.stage_id.name, bold)
                sheet.write(i, 12, obj.x_studio_ultima_nota if(obj.x_studio_ultima_nota) else '', bold)
                sheet.write(i, 13, obj.write_date.strftime("%Y/%m/%d"), bold)
                sheet.write(i, 14, obj.x_studio_tcnico.name if(obj.x_studio_tcnico) else '', bold)
                sheet.write(i, 15, str(str(obj.x_studio_empresas_relacionadas.street_name)+" No. Ext. "+str(obj.x_studio_empresas_relacionadas.street_number)+" No. Int. "+str(obj.x_studio_empresas_relacionadas.street_number2)+" ,COL. "+str(obj.x_studio_empresas_relacionadas.l10n_mx_edi_colony)+" "+str(obj.x_studio_empresas_relacionadas.city)+" México, "+str(obj.x_studio_empresas_relacionadas.state_id.name)+"C.P "+str(obj.x_studio_empresas_relacionadas.zip)), bold)
                sheet.write(i, 16, obj.x_studio_nmero_de_ticket_cliente if(obj.x_studio_nmero_de_ticket_cliente) else '', bold)
                i=i+1
        sheet.add_table('A2:Q'+str(i),{'style': 'Table Style Medium 9','columns': [{'header': 'Ticket'},{'header': 'Tipo de Reporte'},{'header': 'Fecha'},{'header':'Dias de atraso'},{'header': 'Cliente'},{'header': 'Localidad'},{'header': 'Serie'},{'header': 'Modelo'},{'header': 'Area de Atención'},{'header': 'Zona'},{'header': 'Falla'},{'header': 'Último estatus ticket'},{'header': 'Última nota'},{'header': 'Fecha nota'},{'header': 'Tecnico'},{'header': 'Dirección'},{'header': 'No. Ticket cliente'}]}) 
        workbook.close()