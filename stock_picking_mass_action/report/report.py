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
        if(13 in partners.mapped('x_studio_field_aVMhn.id')):
            sheet.merge_range('A1:R1', 'Movimientos de Almacen', merge_format)
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
                if(obj.lot_id!=False):
                    sheet.write(i, 7, obj.lot_id.name, bold)
                sheet.write(i, 8, obj.x_studio_cliente_1 if(obj.x_studio_cliente_1) else '', bold)
                sheet.write(i, 9, obj.x_studio_localidad if(obj.x_studio_localidad) else '', bold)
                sheet.write(i, 10, obj.x_studio_comentarios if(obj.x_studio_comentarios) else '', bold)
                if(obj.x_studio_ticket):
                    sheet.write(i,11, str(obj.x_studio_ticket) if(obj.x_studio_ticket) else '', bold)
                if(obj.x_studio_ticket==False):
                    sheet.write(i, 11, str(obj.x_studio_orden_de_venta) if(obj.x_studio_orden_de_venta) else '', bold)
                sheet.write(i, 12, obj.x_studio_field_y5FBs if(obj.x_studio_field_y5FBs!=0) else '', bold)
                sheet.write(i, 13, obj.x_studio_serie_destino_1 if(obj.x_studio_serie_destino_1) else '', bold)            
                sheet.write(i, 14, obj.x_studio_modelo_equipo if(obj.x_studio_modelo_equipo) else '', bold)                 
                sheet.write(i, 15, obj.x_studio_estado_destino if(obj.x_studio_estado_destino) else '', bold)            
                sheet.write(i, 16, obj.x_studio_colonia_destino if(obj.x_studio_colonia_destino) else '', bold)
                user=self.env['stock.picking'].search(['&',['sale_id','=',obj.picking_id.sale_id.id],['location_id','=',obj.x_studio_field_3lDS0.lot_stock_id.id]])
                if(obj.x_studio_coment):
                    sheet.write(i, 17, obj.x_studio_coment, bold)
                if(obj.x_studio_coment==False):
                    sheet.write(i, 17, user.write_uid.name if(len(user)==1) else user[0].write_uid.name,bold)
                i=i+1
            sheet.add_table('A2:R'+str(i),{'style': 'Table Style Medium 9','columns': [{'header': 'Categoria'},{'header': 'Fecha'},{'header': 'Almacen'},{'header':'Tipo'},{'header': 'Modelo'},{'header': 'No Parte'},{'header': 'Cantidad'},{'header': 'Serie'},{'header': 'Cliente'},{'header': 'Localidad'},{'header': 'Comentario'},{'header': 'Documento Origen'},{'header': 'Numero'},{'header': 'Serie Destino'},{'header': 'Modelo Destino'},{'header': 'Estado'},{'header': 'Delegación'},{'header': 'Usuario'}]})
        if(13 not in partners.mapped('x_studio_field_aVMhn.id')):
            sheet.merge_range('A1:Q1', 'Movimientos de Almacen', merge_format)
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
                sheet.write(i, 7, obj.x_studio_cliente_1 if(obj.x_studio_cliente_1) else '', bold)
                sheet.write(i, 8, obj.x_studio_localidad if(obj.x_studio_localidad) else '', bold)
                sheet.write(i, 9, obj.x_studio_comentarios if(obj.x_studio_comentarios) else '', bold)
                if(obj.x_studio_ticket):
                    sheet.write(i,10, obj.x_studio_ticket if(obj.x_studio_ticket) else '', bold)
                if(obj.x_studio_ticket==False):
                    sheet.write(i, 10, obj.x_studio_orden_de_venta if(obj.x_studio_orden_de_venta) else '', bold)
                sheet.write(i, 11, obj.x_studio_field_y5FBs if(obj.x_studio_field_y5FBs!=0) else '', bold)
                sheet.write(i, 12, obj.x_studio_serie_destino_1 if(obj.x_studio_serie_destino_1) else '', bold)            
                sheet.write(i, 13, obj.x_studio_modelo_equipo if(obj.x_studio_modelo_equipo) else '', bold)                 
                sheet.write(i, 14, obj.x_studio_estado_destino if(obj.x_studio_estado_destino) else '', bold)            
                sheet.write(i, 15, obj.x_studio_colonia_destino if(obj.x_studio_colonia_destino) else '', bold)
                user=self.env['stock.picking'].search(['&',['sale_id','=',obj.picking_id.sale_id.id],['location_id','=',obj.x_studio_field_3lDS0.lot_stock_id.id]])
                if(obj.x_studio_coment):
                    sheet.write(i, 16, obj.x_studio_coment, bold)
                if(obj.x_studio_coment==False):
                    sheet.write(i, 16, user.write_uid.name if(len(user)==1) else user[0].write_uid.name,bold)
                i=i+1
            sheet.add_table('A2:Q'+str(i),{'style': 'Table Style Medium 9','columns': [{'header': 'Categoria'},{'header': 'Fecha'},{'header': 'Almacen'},{'header':'Tipo'},{'header': 'Modelo'},{'header': 'No Parte'},{'header': 'Cantidad'},{'header': 'Cliente'},{'header': 'Localidad'},{'header': 'Comentario'},{'header': 'Documento Origen'},{'header': 'Numero'},{'header': 'Serie Destino'},{'header': 'Modelo Destino'},{'header': 'Estado'},{'header': 'Delegación'},{'header': 'Usuario'}]})
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
            sheet.merge_range('A1:I1', 'Existencias Equipos', merge_format)   
            for obj in quants:
                sheet.write(i, 0, obj.x_studio_almacn.name, bold)
                sheet.write(i, 1, obj.product_id.name, bold)
                sheet.write(i, 2, obj.product_id.default_code, bold)
                sheet.write(i, 3, obj.product_id.description if(obj.product_id.description) else '', bold)
                sheet.write(i, 4, obj.lot_id.name, bold)
                sheet.write(i, 5, obj.lot_id.x_studio_estado, bold)
                sheet.write(i, 6, obj.reserved_quantity, bold)
                sheet.write(i, 7, obj.x_studio_field_kUc4x.x_name if(obj.x_studio_field_kUc4x.x_name) else '', bold)
                precio=self.env['purchase.order.line'].search([['product_id','=',obj.product_id.id]])
                sheet.write(i, 8, precio.sorted(key='id',reverse=True)[0].price_unit if(precio) else obj.product_id.lst_price, bold)
                i=i+1
            sheet.add_table('A2:I'+str((i)),{'style': 'Table Style Medium 9','columns': [{'header': 'Almacen'},{'header': 'Modelo'},{'header': 'No Parte'},{'header':'Descripción'},{'header':'No Serie'},{'header': 'Estado'},{'header': 'Apartados'},{'header': 'Ubicación'},{'header':'Costo'}]}) 
        else:
            sheet = workbook.add_worksheet('Existencias Componentes')
            sheet.merge_range('A1:H1', 'Existencias Componentes', merge_format)   
            for obj in quants:
                sheet.write(i, 0, obj.x_studio_almacn.name, bold)
                sheet.write(i, 1, obj.product_id.name, bold)
                sheet.write(i, 2, obj.product_id.default_code, bold)
                sheet.write(i, 3, obj.product_id.description if(obj.product_id.description) else '', bold)
                sheet.write(i, 4, obj.quantity, bold)
                sheet.write(i, 5, obj.reserved_quantity, bold)
                sheet.write(i, 6, obj.x_studio_field_kUc4x.x_name if(obj.x_studio_field_kUc4x.x_name) else '', bold)
                precio=self.env['purchase.order.line'].search([['product_id','=',obj.product_id.id]])
                sheet.write(i, 7, precio.sorted(key='id',reverse=True)[0].price_unit if(precio) else obj.product_id.lst_price, bold)
                i=i+1
            sheet.add_table('A2:H'+str((i)),{'style': 'Table Style Medium 9','columns': [{'header': 'Almacen'},{'header': 'Modelo'},{'header': 'No Parte'},{'header':'Descripción'},{'header': 'Existencia'},{'header': 'Apartados'},{'header': 'Ubicación'},{'header':'Costo'}]}) 
        workbook.close()


class PartnerXlsx(models.AbstractModel):
    _name = 'report.solicitudes.report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, sale):
        i=2
        d=[]
        if(len(sale)==1 and sale.x_studio_arreglo!='/' and sale.x_studio_arreglo!=False):
            copia=sale
            sale=self.env['sale.order'].browse(eval(sale.x_studio_arreglo)).filtered(lambda x:x.x_area_atencion==True) 
            copia.write({'x_studio_arreglo':'/'})
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'blue'})
        report_name = 'Solicitudes'
        bold = workbook.add_format({'bold': True})
        sheet = workbook.add_worksheet('Solicitudes')
        sheet.merge_range('A1:Q1', 'Solicitudes', merge_format)
        for obj in sale:
            equ=obj.order_line.filtered(lambda x:x.product_id.categ_id.id==13)
            if(len(equ)>1):
                for eq in equ:
                    sheet.write(i, 0, obj.name, bold)
                    sheet.write(i, 1, obj.confirmation_date.strftime("%Y/%m/%d"), bold)
                    sheet.write(i, 2, obj.partner_id.name, bold)
                    sheet.write(i, 3, obj.x_studio_localidades, bold)
                    sheet.write(i, 4, obj.warehouse_id.name, bold)
                    sheet.write(i, 5, obj.x_studio_status if(obj.x_studio_status) else '', bold)
                    sheet.write(i, 6, str(eq.name).split('] ')[1] if(len(eq.name.split('] '))>1) else '', bold)
                    #m=self.env['stock.move.line'].search([['picking_id.sale_id','=',obj.id],['lot_id','=',eq.x_studio_field_9nQhR.id]]).lot_id.name
                    sheet.write(i, 7, str(eq.x_studio_field_9nQhR.name) if(eq.x_studio_field_9nQhR.name) else '', bold)
                    a=obj.order_line.filtered(lambda x:x.product_id.categ_id.id==11).mapped('product_id.name')
                    sheet.write(i, 8, str(a) if(a!=[]) else '', bold)
                    b=obj.order_line.filtered(lambda x:x.product_id.categ_id.id==5).mapped('product_id.name')
                    sheet.write(i, 9, str(b) if(b!=[]) else '', bold)
                    sheet.write(i, 10, len(obj.order_line.filtered(lambda x:x.product_id.categ_id.id==13).mapped('product_id.name')), bold)
                    sheet.write(i, 11, len(obj.order_line.filtered(lambda x:x.product_id.categ_id.id!=13).mapped('product_id.name')), bold)
                    sheet.write(i, 12, obj.x_studio_tipo_de_solicitud if(obj.x_studio_tipo_de_solicitud) else '', bold)
                    sheet.write(i, 13, obj.x_studio_status_1 if(obj.x_studio_status_1) else '', bold)
                    sheet.write(i, 14, obj.x_studio_usuario_creacion_1, bold)
                    sheet.write(i, 15, 'Asignado' if(obj.x_studio_asignado) else 'No Asignado', bold)
                    sheet.write(i, 16, str(obj.note) if(obj.note) else '', bold)
                    i=i+1
            else:
                sheet.write(i, 0, obj.name, bold)
                sheet.write(i, 1, obj.confirmation_date.strftime("%Y/%m/%d") if(obj.confirmation_date) else '', bold)
                sheet.write(i, 2, obj.partner_id.name, bold)
                sheet.write(i, 3, obj.x_studio_localidades, bold)
                sheet.write(i, 4, obj.warehouse_id.name, bold)
                sheet.write(i, 5, obj.x_studio_status if(obj.x_studio_status) else '', bold)
                sheet.write(i, 6, str(equ.name).split('] ')[1] if(len(str(equ.name).split('] '))>1) else '', bold)
                #m=self.env['stock.move.line'].search([['picking_id.sale_id','=',obj.id],['lot_id','=',equ.x_studio_field_9nQhR.id]]).lot_id.name
                sheet.write(i, 7, str(equ.x_studio_field_9nQhR.name) if(equ.x_studio_field_9nQhR.id) else '', bold)
                a=obj.order_line.filtered(lambda x:x.product_id.categ_id.id==11).mapped('product_id.name')
                sheet.write(i, 8, str(a) if(a!=[]) else '', bold)
                b=obj.order_line.filtered(lambda x:x.product_id.categ_id.id==5).mapped('product_id.name')
                sheet.write(i, 9, str(b) if(b!=[]) else '', bold)
                sheet.write(i, 10, len(obj.order_line.filtered(lambda x:x.product_id.categ_id.id==13).mapped('product_id.name')), bold)
                sheet.write(i, 11, len(obj.order_line.filtered(lambda x:x.product_id.categ_id.id!=13).mapped('product_id.name')), bold)
                sheet.write(i, 12, obj.x_studio_tipo_de_solicitud if(obj.x_studio_tipo_de_solicitud) else '', bold)
                sheet.write(i, 13, obj.x_studio_status_1 if(obj.x_studio_status_1) else '', bold)
                sheet.write(i, 14, obj.x_studio_usuario_creacion_1, bold)
                sheet.write(i, 15, 'Asignado' if(obj.x_studio_asignado) else 'No Asignado', bold)
                sheet.write(i, 16, str(obj.note) if(obj.note) else '', bold)
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
        sheet.merge_range('A1:R1', 'Tickets', merge_format)
        for obj in ticket:
            if(len(obj.x_studio_equipo_por_nmero_de_serie_1)==1 or len(obj.x_studio_equipo_por_nmero_de_serie)==1):
                sheet.write(i, 0, obj.name, bold)
                sheet.write(i, 1, obj.x_studio_tipo_de_vale if(obj.x_studio_tipo_de_vale) else '', bold)
                sheet.write(i, 2, obj.create_date.strftime("%Y/%m/%d"), bold)
                sheet.write(i, 3, obj.days_difference, bold)
                sheet.write(i, 4, obj.partner_id.name if(obj.partner_id) else '', bold)
                sheet.write(i, 5, obj.x_studio_empresas_relacionadas.name if(obj.x_studio_empresas_relacionadas) else '', bold)
                sheet.write(i, 6, str(obj.x_studio_equipo_por_nmero_de_serie_1.serie.name) if(obj.team_id.id==8) else str(obj.x_studio_equipo_por_nmero_de_serie.name), bold)
                sheet.write(i, 7, str(obj.x_studio_equipo_por_nmero_de_serie_1.serie.product_id.name) if(obj.team_id.id==8) else str(obj.x_studio_equipo_por_nmero_de_serie.product_id.name), bold)
                p=[]
                if(len(obj.x_studio_equipo_por_nmero_de_serie_1)==1):
                    if(obj.x_studio_equipo_por_nmero_de_serie_1.x_studio_cartuchonefro):
                        p.append(obj.x_studio_equipo_por_nmero_de_serie_1.x_studio_cartuchonefro.name)
                    if(obj.x_studio_equipo_por_nmero_de_serie_1.x_studio_cartucho_amarillo):
                        p.append(obj.x_studio_equipo_por_nmero_de_serie_1.x_studio_cartucho_amarillo.name)
                    if(obj.x_studio_equipo_por_nmero_de_serie_1.x_studio_cartucho_cian_1):
                        p.append(obj.x_studio_equipo_por_nmero_de_serie_1.x_studio_cartucho_cian_1.name)
                    if(obj.x_studio_equipo_por_nmero_de_serie_1.x_studio_cartucho_magenta):
                        p.append(obj.x_studio_equipo_por_nmero_de_serie_1.x_studio_cartucho_magenta.name)
                sheet.write(i, 8, str(obj.x_studio_productos.mapped('name')).replace('[\'','').replace('\']','').replace('\'','') if(len(obj.x_studio_equipo_por_nmero_de_serie)==1) else str(p).replace('[\'','').replace('\']','').replace('\'',''), bold)
                sheet.write(i, 9, obj.team_id.name if(obj.team_id.id) else "", bold)
                sheet.write(i, 10,obj.x_studio_empresas_relacionadas.state_id.name if(obj.x_studio_empresas_relacionadas.state_id) else '' , bold)
                sheet.write(i, 11, obj.description if(obj.description) else '', bold)
                sheet.write(i, 12, obj.stage_id.name if(obj.stage_id.id) else '', bold)
                sheet.write(i, 13, obj.x_studio_ultima_nota if(obj.x_studio_ultima_nota) else '', bold)
                sheet.write(i, 14, obj.write_date.strftime("%Y/%m/%d %H:%M:%S"), bold)
                sheet.write(i, 15, obj.x_studio_tecnico if(obj.x_studio_tecnico) else obj.write_uid.name, bold)
                sheet.write(i, 16, str(str(obj.x_studio_empresas_relacionadas.street_name)+" No. Ext. "+str(obj.x_studio_empresas_relacionadas.street_number)+" No. Int. "+str(obj.x_studio_empresas_relacionadas.street_number2)+" ,COL. "+str(obj.x_studio_empresas_relacionadas.l10n_mx_edi_colony)+" "+str(obj.x_studio_empresas_relacionadas.city)+" México, "+str(obj.x_studio_empresas_relacionadas.state_id.name)+"C.P "+str(obj.x_studio_empresas_relacionadas.zip)), bold)
                sheet.write(i, 17, obj.x_studio_nmero_de_ticket_cliente if(obj.x_studio_nmero_de_ticket_cliente) else '', bold)
                i=i+1
            if(len(obj.x_studio_equipo_por_nmero_de_serie_1)>1 or len(obj.x_studio_equipo_por_nmero_de_serie)>1):
                series=None
                a=False
                if(len(obj.x_studio_equipo_por_nmero_de_serie_1)>1):
                    series=obj.x_studio_equipo_por_nmero_de_serie_1
                    a=True
                if(len(obj.x_studio_equipo_por_nmero_de_serie)>1):
                    series=obj.x_studio_equipo_por_nmero_de_serie
                for s in series:
                    sheet.write(i, 0, obj.name, bold)
                    sheet.write(i, 1, obj.x_studio_tipo_de_vale if(obj.x_studio_tipo_de_vale) else '', bold)
                    sheet.write(i, 2, obj.create_date.strftime("%Y/%m/%d %H:%M:%S"), bold)
                    sheet.write(i, 3, obj.days_difference, bold)
                    sheet.write(i, 4, obj.partner_id.name if(obj.partner_id) else '', bold)
                    sheet.write(i, 5, obj.x_studio_empresas_relacionadas.name if(obj.x_studio_empresas_relacionadas) else '', bold)
                    sheet.write(i, 6, str(s.serie.name) if(a) else str(s.name), bold)
                    sheet.write(i, 7, str(s.serie.product_id.name) if(a) else str(s.name), bold)
                    p=[]
                    if(a):
                        if(s.x_studio_cartuchonefro):
                            p.append(s.x_studio_cartuchonefro.name)
                        if(s.x_studio_cartucho_amarillo):
                            p.append(s.x_studio_cartucho_amarillo.name)
                        if(s.x_studio_cartucho_cian_1):
                            p.append(s.x_studio_cartucho_cian_1.name)
                        if(s.x_studio_cartucho_magenta):
                            p.append(s.x_studio_cartucho_magenta.name)
                    sheet.write(i, 8, str(p).replace('[\'','').replace('\']','').replace('\'','') if(a) else str(obj.x_studio_productos.mapped('name')).replace('[\'','').replace('\']','').replace('\'',''), bold)
                    sheet.write(i, 9, obj.team_id.name if(obj.team_id.id) else "", bold)
                    sheet.write(i, 10,obj.x_studio_empresas_relacionadas.state_id.name if(obj.x_studio_empresas_relacionadas.state_id) else '' , bold)
                    sheet.write(i, 11, obj.description if(obj.description) else '', bold)
                    sheet.write(i, 12, obj.stage_id.name if(obj.stage_id.id) else '', bold)
                    sheet.write(i, 13, obj.x_studio_ultima_nota if(obj.x_studio_ultima_nota) else '', bold)
                    sheet.write(i, 14, obj.write_date.strftime("%Y/%m/%d %H:%M:%S"), bold)
                    sheet.write(i, 15, obj.x_studio_tecnico if(obj.x_studio_tecnico) else obj.write_uid.name, bold)
                    sheet.write(i, 16, str(str(obj.x_studio_empresas_relacionadas.street_name)+" No. Ext. "+str(obj.x_studio_empresas_relacionadas.street_number)+" No. Int. "+str(obj.x_studio_empresas_relacionadas.street_number2)+" ,COL. "+str(obj.x_studio_empresas_relacionadas.l10n_mx_edi_colony)+" "+str(obj.x_studio_empresas_relacionadas.city)+" México, "+str(obj.x_studio_empresas_relacionadas.state_id.name)+"C.P "+str(obj.x_studio_empresas_relacionadas.zip)), bold)
                    sheet.write(i, 17, obj.x_studio_nmero_de_ticket_cliente if(obj.x_studio_nmero_de_ticket_cliente) else '', bold)
                    i=i+1
                else:
                    sheet.write(i, 0, obj.name, bold)
                    sheet.write(i, 1, obj.x_studio_tipo_de_vale if(obj.x_studio_tipo_de_vale) else '', bold)
                    sheet.write(i, 2, obj.create_date.strftime("%Y/%m/%d %H:%M:%S"), bold)
                    sheet.write(i, 3, obj.days_difference, bold)
                    sheet.write(i, 4, obj.partner_id.name if(obj.partner_id) else '', bold)
                    sheet.write(i, 5, obj.x_studio_empresas_relacionadas.name if(obj.x_studio_empresas_relacionadas) else '', bold)
                    sheet.write(i, 6, '', bold)
                    sheet.write(i, 7, '', bold)
                    sheet.write(i, 8, '', bold)
                    sheet.write(i, 9, obj.team_id.name, bold)
                    sheet.write(i, 10, obj.x_studio_empresas_relacionadas.state_id.name if(obj.x_studio_empresas_relacionadas.state_id) else '' , bold)
                    sheet.write(i, 11, obj.description if(obj.description) else '', bold)
                    sheet.write(i, 12, obj.stage_id.name if(obj.stage_id.id) else '', bold)
                    sheet.write(i, 13, obj.x_studio_ultima_nota if(obj.x_studio_ultima_nota) else '', bold)
                    sheet.write(i, 14, obj.write_date.strftime("%Y/%m/%d %H:%M:%S"), bold)
                    sheet.write(i, 15, obj.x_studio_tecnico if(obj.x_studio_tecnico) else obj.write_uid.name, bold)
                    sheet.write(i, 16, str(str(obj.x_studio_empresas_relacionadas.street_name)+" No. Ext. "+str(obj.x_studio_empresas_relacionadas.street_number)+" No. Int. "+str(obj.x_studio_empresas_relacionadas.street_number2)+" ,COL. "+str(obj.x_studio_empresas_relacionadas.l10n_mx_edi_colony)+" "+str(obj.x_studio_empresas_relacionadas.city)+" México, "+str(obj.x_studio_empresas_relacionadas.state_id.name)+"C.P "+str(obj.x_studio_empresas_relacionadas.zip)), bold)
                    sheet.write(i, 17, obj.x_studio_nmero_de_ticket_cliente if(obj.x_studio_nmero_de_ticket_cliente) else '', bold)
        sheet.add_table('A2:R'+str(i),{'style': 'Table Style Medium 9','columns': [{'header': 'Ticket'},{'header': 'Tipo de Reporte'},{'header': 'Fecha'},{'header':'Dias de atraso'},{'header': 'Cliente'},{'header': 'Localidad'},{'header': 'Serie'},{'header': 'Modelo'},{'header': 'Productos'},{'header': 'Area de Atención'},{'header': 'Zona'},{'header': 'Falla'},{'header': 'Último estatus ticket'},{'header': 'Última nota'},{'header': 'Fecha nota'},{'header': 'Tecnico'},{'header': 'Dirección'},{'header': 'No. Ticket cliente'}]}) 
        workbook.close()

class PartnerXlsx(models.AbstractModel):
    _name = 'report.lot_serial.report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lots):
        i=2
        d=[]
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'blue'})
        report_name = 'Base Instalada'
        bold = workbook.add_format({'bold': True})
        sheet = workbook.add_worksheet('Base Instalada')
        sheet.merge_range('A1:X1', 'Base Instalada', merge_format)
        for obj in lots:
            sheet.write(i, 0, obj.servicio.contrato.cliente.name if(obj.servicio) else '', bold)
            sheet.write(i, 1, obj.servicio.contrato.x_studio_grupo if(obj.servicio) else '', bold)
            sheet.write(i, 2, '', bold)
            sheet.write(i, 3, obj.x_studio_locacion_recortada if(obj.servicio) else '', bold)            
            sheet.write(i, 4, obj.name, bold)
            sheet.write(i, 5, obj.product_id.name, bold)
            sheet.write(i, 6, '', bold)
            sheet.write(i, 7, 'Arrendamiento' if(obj.servicio) else '', bold)
            sheet.write(i, 8, obj.servicio.contrato.fechaDeInicioDeContrato.strftime("%Y/%m/%d %H:%M:%S") if(obj.servicio) else '', bold)
            sheet.write(i, 9, obj.servicio.contrato.fechaDeFinDeContrato.strftime("%Y/%m/%d %H:%M:%S") if(obj.servicio) else '', bold)
            sheet.write(i, 10, obj.servicio.contrato.idTechraRef if(obj.servicio) else '', bold)
            sheet.write(i, 11, obj.servicio.idtec if(obj.servicio) else '', bold)
            sheet.write(i, 12, obj.servicio.contrato.cliente.x_studio_vendedor.name if(obj.servicio) else '', bold)
            sheet.write(i, 13, obj.servicio.contrato.cliente.x_studio_ejecutivo.name if(obj.servicio) else '', bold)
            sheet.write(i, 14, obj.servicio.contrato.cliente.street_name if(obj.servicio) else '', bold)
            sheet.write(i, 15, obj.servicio.contrato.cliente.street_number2 if(obj.servicio) else '', bold)
            sheet.write(i, 16, obj.servicio.contrato.cliente.street_number if(obj.servicio) else '', bold)
            sheet.write(i, 17, obj.servicio.contrato.cliente.l10n_mx_edi_colony if(obj.servicio) else '', bold)
            sheet.write(i, 18, obj.servicio.contrato.cliente.city if(obj.servicio) else '', bold)
            sheet.write(i, 19, obj.servicio.contrato.cliente.state_id.name if(obj.servicio) else '', bold)
            sheet.write(i, 20, obj.servicio.contrato.cliente.state_id.name if(obj.servicio) else '', bold)
            sheet.write(i, 21, obj.servicio.contrato.cliente.x_studio_field_SqU5B if(obj.servicio) else '', bold)
            sheet.write(i, 22, 'México' if(obj.servicio) else '', bold)
            sheet.write(i, 23, obj.servicio.contrato.cliente.zip if(obj.servicio) else '', bold)
            i=i+1
        sheet.add_table('A2:X'+str(i),{'style': 'Table Style Medium 9','columns': [{'header': 'NombreCliente'},{'header': 'NombreGrupo'},{'header': 'RFCEmisor'},{'header':'Localidad'},{'header': 'NoSerie'},{'header': 'Modelo'},{'header': 'FechaIngresoCliente'},{'header': 'Tipo'},{'header': 'FechaInicioContrato'},{'header': 'FechaTerminoContrato'},{'header': 'Contrato'},{'header': 'Servicio'},{'header': 'EjecutivoCuenta'},{'header': 'EjecutivoAtencionCliente'},{'header': 'Calle'},{'header': 'No Int'},{'header': 'No Ext'},{'header': 'Colonia'},{'header': 'Delegación'},{'header': 'Ciudad'},{'header': 'Estado'},{'header': 'Zona'},{'header': 'Pais'},{'header': 'Codigo Postal'}]}) 
        workbook.close()