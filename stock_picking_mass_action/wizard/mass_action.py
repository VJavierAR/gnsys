from odoo import _,fields, api
from odoo.models import TransientModel
import datetime, time
from odoo.exceptions import UserError,RedirectWarning
from odoo.tools.float_utils import float_compare
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from pdf2image import convert_from_path, convert_from_bytes
import os
import re
from PyPDF2 import PdfFileMerger, PdfFileReader,PdfFileWriter
from io import BytesIO as StringIO
import base64
import datetime
from odoo.tools.mimetypes import guess_mimetype
import logging, ast
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
_logger = logging.getLogger(__name__)


try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

try:
    from . import odf_ods_reader
except ImportError:
    odf_ods_reader = None

FILE_TYPE_DICT = {
    'text/csv': ('csv', True, None),
    'application/vnd.ms-excel': ('xls', xlrd, 'xlrd'),
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ('xlsx', xlsx, 'xlrd >= 1.0.0'),
    'application/vnd.oasis.opendocument.spreadsheet': ('ods', odf_ods_reader, 'odfpy')
}
EXTENSIONS = {
    '.' + ext: handler
    for mime, (ext, handler, req) in FILE_TYPE_DICT.items()
}

class StockPickingMassAction(TransientModel):
    _name = 'stock.picking.mass.action'
    _description = 'Stock Picking Mass Action'

    @api.model
    def _default_check_availability(self):
        return self.env.context.get('check_availability', False)

    @api.model
    def _default_transfer(self):
        return self.env.context.get('transfer', False)

    def _default_picking_ids(self):
        return self.env['stock.picking'].browse(
            self.env.context.get('active_ids'))

    confirm = fields.Boolean(
        string='Mark as Todo',
        default=True,
        help="check this box if you want to mark as Todo the"
        " selected Pickings.",
    )
    check_availability = fields.Boolean(
        string='Check Availability',
        default=lambda self: self._default_check_availability(),
        help="check this box if you want to check the availability of"
        " the selected Pickings.",
    )
    transfer = fields.Boolean(
        string='Transfer',
        default=lambda self: self._default_transfer(),
        help="check this box if you want to transfer all the selected"
        " pickings.\n You'll not have the possibility to realize a"
        " partial transfer.\n If you want  to do that, please do it"
        " manually on the picking form.",
    )
    picking_ids = fields.Many2many(
        string='Pickings',
        comodel_name="stock.picking",
        default=lambda self: self._default_picking_ids(),
        help="",
    )
    check=fields.Integer(compute='che')
    tecnico=fields.Many2one('hr.employee')

    @api.depends('picking_ids')
    def che(self):
        for s in self.picking_ids:
            #Almacen
            if(s.picking_type_id.id==3):
                self.check=2
            #refacion
            if(s.picking_type_id.id==29314):
                self.check=1
            #ruta
            if(s.picking_type_id.id==2):
                self.check=3
            #distribucion
            if(s.picking_type_id.id==29302):
                self.check=4
    def mass_action(self):
        self.ensure_one()
        # Get draft pickings and confirm them if asked
        if self.confirm:
            draft_picking_lst = self.picking_ids.\
                filtered(lambda x: x.state == 'draft').\
                sorted(key=lambda r: r.scheduled_date)
            draft_picking_lst.sudo().action_confirm()
        # check availability if asked
        if self.check_availability:
            pickings_to_check = self.picking_ids.\
                filtered(lambda x: x.state not in [
                    'draft',
                    'cancel',
                    'done',
                ]).\
                sorted(key=lambda r: r.scheduled_date)
            pickings_to_check.sudo().action_assign()
        # Get all pickings ready to transfer and transfer them if asked
        if self.transfer:
            _logger.info("Hola ando subiendo info ya te avise en el grupo y en privadoxD")
            assigned_picking_lst = self.picking_ids.\
                filtered(lambda x: x.state == 'assigned').\
                sorted(key=lambda r: r.scheduled_date)
            assigned_picking_lst2 = self.picking_ids.\
                filtered(lambda x: x.picking_type_id.id == 3 and x.state == 'assigned')
            quantities_done = sum(
                move_line.qty_done for move_line in
                assigned_picking_lst.mapped('move_line_ids').filtered(
                    lambda m: m.state not in ('done', 'cancel')))
            CON=str(self.env['ir.sequence'].next_by_code('concentrado'))
            for l in assigned_picking_lst:
                if(l.picking_type_id.id==3):
                    self.check=2
                    #l.sudo().write({'concentrado':CON})
                    self.env['stock.picking'].search([['sale_id','=',l.sale_id.id]]).write({'concentrado':CON})
                if(l.picking_type_id.id==29314):
                    self.check=1
            pick_to_backorder = self.env['stock.picking']
            pick_to_do = self.env['stock.picking']
            for picking in assigned_picking_lst:
                # If still in draft => confirm and assign
                if picking.state == 'draft':
                    picking.action_confirm()
                    if picking.state != 'assigned':
                        picking.action_assign()
                        if picking.state != 'assigned':
                            raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
                for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                    for move_line in move.move_line_ids:
                        move_line.qty_done = move_line.product_uom_qty
                if picking._check_backorder():
                    pick_to_backorder |= picking
                    continue
                pick_to_do |= picking
            if pick_to_do:
                pick_to_do.action_done()
            if assigned_picking_lst._check_backorder():
                cancel_backorder=True
                if cancel_backorder:
                   for pick_id in self.picking_ids:
                       moves_to_log = {}
                       for move in pick_id.move_lines:
                           if float_compare(move.product_uom_qty, move.quantity_done, precision_rounding=move.product_uom.rounding) > 0:
                               moves_to_log[move] = (move.quantity_done, move.product_uom_qty)
                       pick_id._log_less_quantities_than_expected(moves_to_log)
                self.picking_ids.action_done()
                if cancel_backorder:
                    for pick_id in self.picking_ids:
                        backorder_pick = self.env['stock.picking'].search([('backorder_id', '=', pick_id.id)])
                        if(pick_id.picking_type_id.id==3 or pick_id.picking_type_id.id==29314):

                            sale = self.env['sale.order'].create({'x_studio_backorder':True,'partner_id' : backorder_pick.sale_id.partner_id.id, 'origin' : backorder_pick.sale_id.origin, 'x_studio_tipo_de_solicitud' : 'Venta', 'x_studio_requiere_instalacin' : True, 'x_studio_field_RnhKr': backorder_pick.sale_id.x_studio_field_RnhKr.id, 'partner_shipping_id' : backorder_pick.sale_id.partner_shipping_id.id, 'warehouse_id' :backorder_pick.sale_id.warehouse_id.id, 'team_id' : 1, 'x_studio_field_bxHgp': pick_id.x_studio_ticket_relacionado.id})
                            pick_id.write({'sale_child':sale.id})
                            for rr in backorder_pick.move_ids_without_package:
                                datosr={'order_id' : sale.id, 'product_id' : rr.product_id.id, 'product_uom_qty' :rr.product_uom_qty,'x_studio_field_9nQhR':rr.x_studio_serie_destino.id, 'price_unit': 0}
                                if(pick_id.x_studio_ticket_relacionado.team_id.id==10 or pick_id.x_studio_ticket_relacionado.team_id.id==11):
                                    datosr['route_id']=22548
                                self.env['sale.order.line'].create(datosr)
                            pick_id.x_studio_ticket_relacionado.write({'x_studio_field_0OAPP':[(4,sale.id)]})
                            sale.sudo().action_confirm()
                        backorder_pick.action_cancel()
            if(len(assigned_picking_lst2)>0):
                return self.env.ref('stock_picking_mass_action.report_custom').report_action(assigned_picking_lst2)
        #return {'type': 'ir.actions.client','tag': 'reload'}


    @api.multi
    def vales(self):
        assigned_picking_lst2 = self.picking_ids.\
        filtered(lambda x: x.picking_type_id.id == 3 and x.state == 'done')
        return self.env.ref('studio_customization.vale_de_entrega_56cdb2f0-51e3-447e-8a67-6e5c7a6b3af9').report_action(assigned_picking_lst2)
    @api.multi
    def etiquetas(self):
        assigned_picking_lst2 = self.picking_ids.\
        filtered(lambda x: x.picking_type_id.id == 3 and x.state == 'done')
        return self.env.ref('studio_customization.transferir_reporte_4541ad13-9ccb-4a0f-9758-822064db7c9a').report_action(assigned_picking_lst2)


class StockCambio(TransientModel):
    _name = 'cambio.toner'
    _description = 'Cambio toner'
    pick=fields.Many2one('stock.picking')
    pro_ids = fields.One2many('cambio.toner.line','rel_cambio')

    def confirmar(self):
        if(self.pick.sale_id):
            i=0
            self.pick.backorder=''
            dt=[]
            al=[]
            for sa in self.pick.move_ids_without_package:
                d=list(filter(lambda x:x['producto1']['id']==sa.product_id.id,self.pro_ids))
                if(d!=[]):
                    if(sa.product_id.id!=d[0]['producto2']['id']):
                        self.env.cr.execute("delete from stock_move_line where reference='"+self.pick.name+"' and product_id="+str(sa.product_id.id)+";")
                        self.env.cr.execute("delete from stock_move where origin='"+self.pick.sale_id.name+"' and product_id="+str(sa.product_id.id)+";")
                        self.env.cr.execute("delete from sale_order_line where id="+str(sa.id)+" and product_id="+str(sa.product_id.id)+";")
                        if(i==0):
                            self.env.cr.execute("update stock_picking set state='draft' where sale_id="+str(self.pick.sale_id.id)+";")
                        i=i+1
                        #l=self.env['stock.production.lot'].search([['name','=',d[0]['serie']]])
                        datos={'x_studio_field_9nQhR':d[0]['serie']['id'],'order_id':self.pick.sale_id.id,'product_id':d[0]['producto2']['id'],'product_uom':d[0]['producto2']['uom_id']['id'],'product_uom_qty':d[0]['cantidad'],'name':d[0]['producto2']['description'] if(d[0]['producto2']['description']) else '/','price_unit':0.00}
                        ss=self.env['sale.order.line'].sudo().create(datos)
                        if(d[0]['almacen']['id']):
                            self.env['stock.move'].search([['sale_id','=',self.pick.sale_id.id],['product_id','=',d[0]['producto2']['id']]]).write({'location_id':d[0]['almacen']['lot_stock_id']['id']})
                    else:
                        if(d[0]['almacen']['id']):
                            self.env['stock.move'].search([['origin','=',str(self.pick.sale_id.name)],['product_id','=',d[0]['producto2']['id']]]).write({'location_id':d[0]['almacen']['lot_stock_id']['id']})
            self.pick.action_confirm()
            self.pick.action_assign()
            """
            for prp in self.pro_ids:
                if(prp.producto1.id !=prp.producto2.id):
                    dt.append(prp.producto1.id)
                    dat={'producto':prp.producto1.id,'almacen':prp.almacen.lot_stock_id.id}
                    al.append(dat)
            for s in self.pick.sale_id.order_line:
                if(s.product_id.id in dt):
                    i=i+1

            if(i>0):
                self.env.cr.execute("update stock_picking set state='draft' where sale_id="+str(self.pick.sale_id.id)+";")
                for li in self.pro_ids:
                    if(s.product_id.id in dt):
                        l=self.env['stock.production.lot'].search([['name','=',li.serie]])
                        datos={'x_studio_field_9nQhR':l.id,'order_id':self.pick.sale_id.id,'product_id':li.producto2.id,'product_uom':li.producto2.uom_id.id,'product_uom_qty':li.cantidad,'name':li.producto2.description if(li.producto2.description) else '/','price_unit':0.00}
                        ss=self.env['sale.order.line'].sudo().create(datos)
            
            for p1 in self.pick.move_ids_without_package:
                    if(i>0):
                    else:
                        if()

                    if(p1.product_id.id in dt):
                            alm2=list(filter(lambda x:x['producto']==p1.product_id.id,al))
                            if(alm2!=[]):
                                p1.write({'location_id':alm2[0]['almacen']})
            """





class StockCambioLine(TransientModel):
    _name = 'cambio.toner.line'
    _description = 'Lineas cambio toner'
    producto1=fields.Many2one('product.product')
    producto2=fields.Many2one('product.product')
    cantidad=fields.Float()
    rel_cambio=fields.Many2one('cambio.toner')
    serie=fields.Many2one('stock.production.lot')
    almacen=fields.Many2one('stock.warehouse',string='Almacen')
    existencia1=fields.Integer(compute='nuevo',string='Existencia Nuevo')
    existencia2=fields.Integer(compute='nuevo',string='Existencia Usado')
    existeciaAlmacen=fields.Integer(compute='almac',string='Existencia de Almacen seleccionado')
    tipo=fields.Integer()
    
    @api.depends('producto1')
    def nuevo(self):
        for record in self:
            ex=self.env['stock.quant'].search([['location_id','=',12],['product_id','=',record.producto1.id]]).sorted(key='quantity',reverse=True)
            record.existencia1=int(ex[0].quantity) if(len(ex)>0) else 0
            ex2=self.env['stock.quant'].search([['location_id','=',41917],['product_id','=',record.producto1.id]]).sorted(key='quantity',reverse=True)
            record.existencia2=int(ex2[0].quantity) if(len(ex2)>0) else 0
    
    @api.depends('almacen')
    def almac(self):
        for record in self:
            if(record.almacen):
                ex=self.env['stock.quant'].search([['location_id','=',record.almacen.lot_stock_id.id],['product_id','=',record.producto1.id]]).sorted(key='quantity',reverse=True)
                record.existeciaAlmacen=int(ex[0].quantity) if(len(ex)>0) else 0 

class GuiaTicket(TransientModel):
    _name = 'guia.ticket'
    _description = 'Guias de Ticket'
    guia=fields.Char(string='Guia')
    pick=fields.Many2one('stock.picking')

    def confirmar(self):
        if(self.guia):
            self.pick.write({'carrier_tracking_ref':self.guia})
            if(self.pick.sale_id.x_studio_field_bxHgp):
                self.pick.sale_id.x_studio_field_bxHgp.sudo().write({'x_studio_nmero_de_guia_1': self.guia})
                self.env['helpdesk.diagnostico'].sudo().create({ 'ticketRelacion' : self.pick.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id, 'estadoTicket' : "Guia Agregada", 'comentario':"Guia: "+self.guia}) 



class ComemtarioTicket(TransientModel):
    _name = 'comentario.ticket'
    _description = 'Comemtario de Ticket'
    comentario=fields.Char(string='Comentario')
    evidencia=fields.Many2many('ir.attachment', string="Evidencias")
    pick=fields.Many2one('stock.picking')
    ruta=fields.Integer(related='pick.ruta_id.id')

    def confirmar(self):
        if(self.ruta==False):
            self.pick.x_studio_evidencia_a_ticket=self.evidencia
            self.pick.x_studio_comentario_1=self.comentario
            self.env['helpdesk.diagnostico'].sudo().create({ 'ticketRelacion' : self.pick.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id, 'estadoTicket' : "Devuelto a Distribución", 'comentario':self.comentario}) 
        else:
            self.pick.x_studio_evidencia_a_ticket=self.evidencia
            self.pick.x_studio_comentario_1=self.comentario
            self.env['helpdesk.diagnostico'].create({'ticketRelacion': self.pick.sale_id.x_studio_field_bxHgp.id
                                        ,'comentario': self.comentario
                                        ,'estadoTicket': self.pick.sale_id.x_studio_field_bxHgp.stage_id.name
                                        ,'evidencia': [(6,0,self.evidencia.ids)]
                                        ,'mostrarComentario': False
                                        })

class TransferInter(TransientModel):
    _name='transferencia.interna'
    _description='Transferencia Interna'    
    almacenPadre=fields.Many2one('stock.warehouse','Almacen Padre')
    almacenOrigen=fields.Many2one('stock.warehouse','Almacen Hijo',domain="[('x_studio_almacn_padre','=',almacenPadre)]")
    ubicacion=fields.Many2one(related='almacenOrigen.lot_stock_id')
    almacenDestino=fields.Many2one('stock.warehouse','Almacen Destino')
    lines=fields.One2many('transferencia.interna.temp','transfer')
    categoria=fields.Many2one('product.category','Categoria de productos')

    def confirmar(self):
        pick_dest=[]
        pick_origin=[]
        pick_origin1=[]
        pick_origin2=[]
        pick_origin3=[]
        if(self.almacenOrigen.id==False):
            self.almacenOrigen=self.almacenPadre.id

        if(self.almacenDestino.x_studio_almacn_padre):
            if('Foraneo' in self.almacenDestino.x_studio_almacn_padre.name):
                origen1=None
                if(self.almacenOrigen.id==1):
                    origen1=self.env['stock.picking.type'].search([['name','=','Surtir'],['warehouse_id','=',self.almacenOrigen.id]])
                if(self.almacenOrigen.id!=1):
                    origen1=self.env['stock.picking.type'].search([['name','=','Pick'],['warehouse_id','=',self.almacenOrigen.id]])
                origen2=self.env['stock.picking.type'].search([['name','=','Distribución'],['warehouse_id','=',1]])
                origen3=self.env['stock.picking.type'].search([['name','=','Tránsito'],['warehouse_id','=',1]])
                destino=self.env['stock.picking.type'].search([['name','=','Receipts'],['warehouse_id','=',self.almacenDestino.id]])
                pick_origin1= self.env['stock.picking'].create({'internas':True,'picking_type_id' : origen1.id,'almacenOrigen':self.almacenOrigen.id,'almacenDestino':self.almacenDestino.id,'location_id':origen1.default_location_src_id.id,'location_dest_id':origen2.default_location_src_id.id})
                pick_origin2= self.env['stock.picking'].create({'internas':True,'picking_type_id' : origen2.id,'almacenOrigen':self.almacenOrigen.id,'almacenDestino':self.almacenDestino.id,'location_id':origen2.default_location_src_id.id,'location_dest_id':origen3.default_location_src_id.id})
                pick_origin3= self.env['stock.picking'].create({'internas':True,'picking_type_id' : origen3.id,'almacenOrigen':self.almacenOrigen.id,'almacenDestino':self.almacenDestino.id,'location_id':origen3.default_location_src_id.id,'location_dest_id':17})
                pick_dest = self.env['stock.picking'].create({'internas':True,'picking_type_id' : destino.id, 'location_id':17,'almacenOrigen':self.almacenOrigen.id,'almacenDestino':self.almacenDestino.id,'location_dest_id':self.almacenDestino.lot_stock_id.id})
        else:    
            origen=self.env['stock.picking.type'].search([['name','=','Internal Transfers'],['warehouse_id','=',self.almacenOrigen.id]])
            destino=self.env['stock.picking.type'].search([['name','=','Internal Transfers'],['warehouse_id','=',self.almacenDestino.id]])
            pick_origin = self.env['stock.picking'].create({'internas':True,'picking_type_id' : origen.id,'almacenOrigen':self.almacenOrigen.id,'almacenDestino':self.almacenDestino.id,'location_id':self.almacenOrigen.lot_stock_id.id,'location_dest_id':17})
            pick_dest = self.env['stock.picking'].create({'internas':True,'picking_type_id' : destino.id, 'location_id':17,'almacenOrigen':self.almacenOrigen.id,'almacenDestino':self.almacenDestino.id,'location_dest_id':self.almacenDestino.lot_stock_id.id})
        v=0
        e=[]
        e1=[]
        for l in self.lines:
            datos1={'product_id' : l.producto.id, 'product_uom_qty' : l.cantidad,'name':l.producto.description if(l.producto.description) else '/','product_uom':l.unidad.id,'location_id':self.almacenOrigen.lot_stock_id.id,'location_dest_id':17}
            datos2={'product_id' : l.producto.id, 'product_uom_qty' : l.cantidad,'name':l.producto.description if(l.producto.description) else '/','product_uom':l.unidad.id,'location_id':17,'location_dest_id':self.almacenDestino.lot_stock_id.id}
            if(self.almacenDestino.x_studio_almacn_padre):
                if('Foraneo' in self.almacenDestino.x_studio_almacn_padre.name):
                    datos1['picking_id']=pick_origin1.id
                    datos1['location_id']=pick_origin1.location_id.id
                    datos1['location_dest_id']=pick_origin1.location_dest_id.id
                    self.env['stock.move'].create(datos1)
                    #2
                    datos1['picking_id']=pick_origin2.id
                    datos1['location_id']=pick_origin2.location_id.id
                    datos1['location_dest_id']=pick_origin2.location_dest_id.id
                    self.env['stock.move'].create(datos1)
                    #3
                    datos1['picking_id']=pick_origin3.id
                    datos1['location_id']=pick_origin3.location_id.id
                    datos1['location_dest_id']=pick_origin3.location_dest_id.id
                    self.env['stock.move'].create(datos1)

                    datos2['picking_id']=pick_dest.id
                    self.env['stock.move'].create(datos2)

            else:
                datos1['picking_id']= pick_origin.id
                datos2['picking_id']= pick_dest.id
                a=self.env['stock.move'].create(datos1)
                b=self.env['stock.move'].create(datos2)
                pick_origin.action_confirm()
                pick_origin.action_assign()
                pick_dest.action_confirm()
                pick_dest.action_assign()
                pick_origin.action_confirm()
                pick_origin.action_assign()
                pick_dest.action_confirm()
                pick_dest.action_assign()
            if(l.producto.categ_id.id==13):
                v=1
                e.append(a.id)
                e1.append(b.id)

        #if(v==1):
        #    p=self.lines.filtered(lambda x:x.producto.categ_id.id==13).sorted(key='id')
        #    e2=self.env['stock.move.line'].search([['move_id','in',e]]).sorted(key='move_id')
        #    e3=self.env['stock.move.line'].search([['move_id','in',e1]]).sorted(key='move_id')
        #    for ee in p:
        #      e2.write({'lot_id':ee.serie.id})
        #      e3.write({'lot_id':ee.serie.id})  
  
        name = 'Picking'
        res_model = 'stock.picking' 
        view_name = 'stock.view_picking_form'
        view = self.env.ref(view_name)
        return {
            'name': _('Transferencia'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            #'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'current',
            'res_id': pick_origin.id if(pick_origin!=[]) else pick_origin1.id,
            'nodestroy': True
        }




class TransferInterMoveTemp(TransientModel):
    _name='transferencia.interna.temp'
    _description='Lineas Temporales Transferencia'
    producto=fields.Many2one('product.product')
    modelo=fields.Char(related='producto.name',string='Modelo')
    noParte=fields.Char(related='producto.default_code',string='No. Parte')
    descripcion=fields.Text(related='producto.description',string='Descripción')
    stoc=fields.Many2one('stock.quant',string='Existencia')
    cantidad=fields.Integer('Demanda Inicial')
    almacen=fields.Many2one('stock.warehouse','Almacén Origen')
    ubicacion=fields.Many2one('stock.location','Ubicación')
    disponible=fields.Float(related='stoc.quantity',string='Disponible')
    transfer=fields.Many2one('transferencia.interna')
    unidad=fields.Many2one('uom.uom',related='producto.uom_id')
    categoria=fields.Many2one('product.category')
    serie=fields.Many2one('stock.production.lot',store=True)

    #lock=fields.Boolean('lock')
    #serieDestino=fields.Many2one('stock.production.lot')

    @api.onchange('producto')
    def quant(self):
        res={}
        if(self.producto):
            self.disponible=0
            h=self.env['stock.quant'].search([['product_id','=',self.producto.id],['location_id','=',self.ubicacion.id],['quantity','>',0]])
            if(len(h)>0 and self.producto.categ_id.id!=13):
                self.stoc=h.id
            if(len(h)==0 and self.producto.categ_id.id!=13):
                d=self.env['stock.location'].search([['location_id','=',self.ubicacion.id]])
                for di in d:
                    i=self.env['stock.quant'].search([['product_id','=',self.producto.id],['location_id','=',di.id],['quantity','>',0]])
                    if(len(i)>0):
                        self.stoc=i.id
            if(self.producto.categ_id.id==13):
                self.disponible=len(h)
                self.cantidad=1
                res['domain']={'serie':[('id','in',h.mapped('lot_id.id'))]}
                return res
                

class PickingSerie(TransientModel):
    _name='picking.serie'
    _description='Seleccion Serie'    
    pick=fields.Many2one('stock.picking')
    lines=fields.One2many('picking.serie.line','rel_picki_serie')


    def confirmar(self):
        for s in self.lines:
            d=self.env['stock.move.line'].search([['move_id','=',s.move_id.id]])
            d.write({'lot_id':s.serie.id})
        return 0

class PickingSerieLine(TransientModel):
    _name='picking.serie.line'
    _description='lines temps'
    producto=fields.Many2one('product.product')
    serie=fields.Many2one('stock.production.lot',domain="['&',('product_id.id','=',producto),('x_studio_estado','=',estado)]")
    estado=fields.Selection([["Obsoleto","Obsoleto"],["Usado","Usado"],["Hueso","Hueso"],["Para reparación","Para reparación"],["Nuevo","Nuevo"],["Buenas condiciones","Buenas condiciones"],["Excelentes condiciones","Excelentes condiciones"],["Back-up","Back-up"],["Dañado","Dañado"]])
    modelo=fields.Many2one(related='serie.product_id')
    rel_picki_serie=fields.Many2one('picking.serie')
    color=fields.Selection([('B/N','B/N'),('Color', 'Color')])
    contadorMono=fields.Integer('Contador Monocromatico')
    contadorColor=fields.Integer('Contador Color')
    move_id=fields.Many2one('stock.move')
    @api.onchange('producto')
    def color(self):
        if(self.producto):
            self.color=self.producto.x_studio_color_bn

class StockPickingMassAction(TransientModel):
    _name = 'stock.move.action'
    _description = 'Reporte de Movimientos'
    picking_ids = fields.Many2many(comodel_name="stock.move")
    almacen=fields.Many2one('stock.warehouse')
    categoria=fields.Many2one('product.category')
    tipo=fields.Selection([["Entrada","Entrada"],["Salida","Salida"],["Todos","Todos"]],default="Todos")
    fechaInicial=fields.Datetime()
    fechaFinal=fields.Datetime()

    def report(self):
        move=None
        mov=self.env['stock.move.line'].search(['&','&',['state','=','done'],['date','>=',self.fechaInicial],['date','<=',self.fechaFinal]])
        move=mov
        origenes=[]
        destinos=[]
        _logger.info('info'+str(len(move)))
        if(self.almacen.id==False):
            almacenes=self.env['stock.warehouse'].search([['x_studio_cliente','=',False]])
            for alm in almacenes:
                b=alm.wh_output_stock_loc_id.id
                c=alm.wh_input_stock_loc_id.id
                if(self.tipo=="Todos"):
                    origenes.append(b)
                    destinos.append(c)
                if(self.tipo=="Entrada"):
                    destinos.append(c)
                if(self.tipo=="Salida"):
                    origenes.append(b)
        if(self.almacen.id):
            b=self.almacen.wh_output_stock_loc_id.id
            c=self.almacen.wh_input_stock_loc_id.id
            if(self.tipo=="Todos"):
                origenes.append(b)
                destinos.append(c)
            if(self.tipo=="Entrada"):
                destinos.append(c)
            if(self.tipo=="Salida"):
                origenes.append(b)
        if(self.categoria):
            mov=mov.filtered(lambda x: x.x_studio_field_aVMhn.id==self.categoria.id)
        _logger.info('info'+str(len(mov)))
        if(self.categoria==False):
            categorias=self.env['product.category'].search([['id','!=',13]]).mapped('id')
            mov=mov.filtered(lambda x: x.x_studio_field_aVMhn.id in categorias)
        _logger.info('info'+str(len(mov)))
        mov=mov.filtered(lambda x: x.location_id.id in origenes or x.location_dest_id.id in destinos)
        _logger.info('info'+str(len(mov)))
        if(len(mov)>1):
            mov[0].write({'x_studio_arreglo':mov.mapped('id')})
            return self.env.ref('stock_picking_mass_action.partner_xlsx').report_action(mov[0])
        if(len(mov)==0):
            raise UserError(_("No hay registros para la selecion actual"))

class StockQuantMassAction(TransientModel):
    _name = 'stock.quant.action'
    _description = 'Reporte de Existencias'
    quant_ids = fields.Many2many(comodel_name="stock.quant")
    almacen=fields.Many2many('stock.warehouse')
    categoria=fields.Many2one('product.category')
    tipo=fields.Many2one('product.product',string='Modelo')
    equipo =fields.Boolean('Equipos')
    estado=fields.Selection([["Obsoleto","Obsoleto"],["Usado","Usado"],["Hueso","Hueso"],["Para reparación","Para reparación"],["Nuevo","Nuevo"],["Buenas condiciones","Buenas condiciones"],["Excelentes condiciones","Excelentes condiciones"],["Back-up","Back-up"],["Dañado","Dañado"]])
    #almacenes=fields.Many2many('stock.warehouse')


    #@api.onchange('almacen')
    #def cambio(self):
    #    if(self.almacen):
    #        self.almacenes=[(4,self.almacen.id)]



    def report(self):
        d=[]
        # if(self.equipo):
        #     d.append(['x_studio_almacn.x_studio_cliente','=',False])
        #     if(self.almacen):
        #         d.append(['x_studio_almacn','=',self.almacen.id])
        #     if(self.almacen.id==False):
        #         d.append(['x_studio_almacn','!=',False])
        #     #d.append(['lot_id','!=',False])
        # else:
        if(len(self.almacen)>0):
            d.append(['x_studio_almacn','in',self.almacen.mapped('id')])
        if(self.categoria):
            d.append(['x_studio_categoria','=',self.categoria.id])
            if(self.categoria.id==13):
                d.append(['x_studio_almacn.x_studio_cliente','=',False])
                if(self.almacen):
                    d.append(['x_studio_almacn','=',self.almacen.id])
                if(self.almacen.id==False):
                    d.append(['x_studio_almacn','!=',False])
        if(self.tipo):
            d.append(['product_id','=',self.tipo.id])
        if(self.estado):
            d.append(['lot_id.x_studio_estado','=',self.estado])
            # if(self.almacen.id==False):
            #     d.append(['x_studio_almacn','!=',False])
            # if(self.categoria.id==False):
            #     d.append(['x_studio_categoria','!=',False])
            # if(self.tipo.id==False):
            #     d.append(['product_id','!=',False])
            #d.append(['x_studio_almacn.x_studio_cliente','=',False])
            #d.append(['lot_id','=',False])
        _logger.info(str(d))
        data=self.env['stock.quant'].search(d,order="x_studio_almacn")
        #_logger.info(str(data.mapped('id')))
        if(len(data)>0):
            data[0].write({'x_studio_arreglo':str(data.mapped('id'))})
            return self.env.ref('stock_picking_mass_action.quant_xlsx').report_action(data[0])        
        if(len(data)==0):
            raise UserError(_("No hay registros para la selecion actual"))
class SaleOrderMassAction(TransientModel):
    _name = 'sale.order.action'
    _description = 'Reporte de Solicitudes'
    fechaInicial=fields.Datetime()
    fechaFinal=fields.Datetime()

    def report(self):
        i=[]
        d=[]
        if(self.fechaInicial):
            m=['confirmation_date','>=',self.fechaInicial]
            i.append(m)
        if(self.fechaFinal):
            m=['confirmation_date','<=',self.fechaFinal]
            i.append(m)
        i.append(['x_studio_field_bxHgp','=',False])
        d=self.env['sale.order'].search(i,order='confirmation_date asc').filtered(lambda x:x.origin==False and x.x_studio_factura==False and len(x.order_line)>0)
        _logger.info(str(len(d)))
        if(len(d)>0):
            d[0].write({'x_studio_arreglo':str(d.mapped('id'))})
            return self.env.ref('stock_picking_mass_action.sale_xlsx').report_action(d[0])
        if(len(d)==0):
            raise UserError(_("No hay registros para la selecion actual"))

class HelpdeskTicketMassAction(TransientModel):
    _name = 'helpdesk.ticket.action'
    _description = 'Reporte de Tickets'
    fechaInicial=fields.Datetime()
    fechaFinal=fields.Datetime()
    estado=fields.Many2one('helpdesk.state')
    tipo=fields.Selection([["Falla","Falla"],["Toner","Toner"]])
    area=fields.Many2one('helpdesk.team')
    def report(self):
        i=[]
        d=[]
        j=[]
        if(self.fechaInicial):
            m=['create_date','>=',self.fechaInicial]
            i.append(m)
        if(self.fechaFinal):
            m=['create_date','<=',self.fechaFinal]
            i.append(m)
        j.append('|')
        if(self.tipo):
            if(self.tipo=="Toner"):
                #m=['x_studio_tipo_de_vale','=','Falla']
                #i.append(m)
                m=['team_id.id','=',8]
                i.append(m)
                #j.append('&')
            else:
                #m=['x_studio_tipo_de_vale','=','Requerimiento']
                #i.append(m)
                m=['team_id.id','!=',8]
                i.append(m)
                #j.append('&')
        if(self.tipo==False):
            m=['x_studio_tipo_de_vale','in',['Requerimiento','Falla']]
            i.append(m)
        #for ii in range(len(i)-2):
        #    j.append('&')
        i.append(['x_studio_field_nO7Xg','!=',False])
        #j.extend(i)

        d=self.env['helpdesk.ticket'].search(i,order='create_date asc').filtered(lambda x:len(x.x_studio_equipo_por_nmero_de_serie_1)>0 or len(x.x_studio_equipo_por_nmero_de_serie)>0)
        if(len(d)>0):
            d[0].write({'x_studio_arreglo':str(d.mapped('id'))})
            return self.env.ref('stock_picking_mass_action.ticket_xlsx').report_action(d[0])
        if(len(d)==0):
            raise UserError(_("No hay registros para la selecion actual"))


class SolicitudestockInventoryMassAction(TransientModel):
    _name = 'stock.inventory.action'
    _description = 'Importacion Inventario'
    almacen=fields.Many2one('stock.warehouse',domain="[('x_studio_cliente','=',False)]")
    archivo=fields.Binary()
    comentario=fields.Char()


    def importacion(self):
        if(self.archivo):
            f2=base64.b64decode(self.archivo)
            H=StringIO(f2)
            mimetype = guess_mimetype(f2 or b'')
            _logger.info(str(mimetype))
            if(mimetype=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or mimetype=='application/vnd.ms-excel'):
                book = xlrd.open_workbook(file_contents=f2 or b'')
                sheet = book.sheet_by_index(0)
                header=[]
                arr=[]
                i=0
                id3=self.env['stock.inventory'].create({'name':str(self.comentario)+' '+str(self.almacen.name), 'location_id':self.almacen.lot_stock_id.id,'x_studio_field_8gltH':self.almacen.id,'state':'done'})
                for row_num, row in enumerate(sheet.get_rows()):
                    if(i>0):
                        ubicacion=None
                        template=self.env['product.template'].search([('default_code','=',str(row[1].value).replace('.0',''))])
                        productid=self.env['product.product'].search([('product_tmpl_id','=',template.id)])
                        quant={'product_id':productid.id,'reserved_quantity':'0','quantity':row[2].value, 'location_id':self.almacen.lot_stock_id.id}
                        inventoty={'inventory_id':id3.id, 'partner_id':'1','product_id':productid.id,'product_uom_id':'1','product_qty':row[2].value, 'location_id':self.almacen.lot_stock_id.id}
                        if(row[3].ctype!=0):
                            ubicacion=self.env['x_ubicacion_inventario'].search([('x_name','=',str(row[3].value).replace('.0',''))])
                        if(len(ubicacion)>0):
                            inventory['x_studio_field_yVDjd']=ubicacion.id
                        self.env['stock.inventory.line'].create(inventoty)
                        busqueda=self.env['stock.quant'].search([['product_id','=',productid.id],['location_id','=',self.almacen.lot_stock_id.id]])
                        _logger.info(str(busqueda))
                        if(busqueda.id):
                            if(len(ubicacion)>0):
                                busqueda.sudo().write({'quantity':row[2].value,'x_studio_field_kUc4x':ubicacion.id})                            
                            else:
                                busqueda.sudo().write({'quantity':row[2].value})
                        if(busqueda.id==False):
                            if(len(ubicacion)>0):
                                quant['x_studio_field_kUc4x']=ubicacion.id
                            else:
                                self.env['stock.quant'].sudo().create(quant)
                    i=i+1
            else:
                raise UserError(_("Archivo invalido"))

class PickingsAComprasMassAction(TransientModel):
    _name = 'stock.pickings.compras'
    _description = 'Picking a compras'
    
    def _default_picking_ids(self):
        return self.env['stock.picking'].browse(
            self.env.context.get('active_ids'))

    picking_ids = fields.Many2many(
        string='Pickings',
        comodel_name="stock.picking",
        default=lambda self: self._default_picking_ids(),
        help="",
    )

    def confirmar(self):
        _logger.info("Test")
        requLin=[]
        pi=[]
        requisiociones=self.env['requisicion.requisicion'].search([])
        test=requisiociones.mapped('picking_ids.id')
        _logger.info(str(test))
        for pick in self.picking_ids:
            e=[]
            if(pick.id not in test):
                for move in pick.move_ids_without_package:
                    d=self.env['stock.quant'].search([['location_id','=',move.location_id.id],['product_id','=',move.product_id.id]]).sorted(key='quantity',reverse=True)
                    if(d.quantity==0):
                        requisicionline={'cliente':move.picking_id.partner_id.id,'ticket':move.picking_id.x_studio_ticket_relacionado.id,'product':move.product_id.id,'cantidad':move.product_uom_qty,'costo':0}
                        #i=self.env['product.rel.requisicion'].create(requisicionline)
                        requLin.append(requisicionline)
                        e.append(move.picking_id.id)
                if(e!=[]):
                    pi.append(e[0])
        if(len(requLin)>0):
            requisicion=self.env['requisicion.requisicion'].create({'area':'Almacen','fecha_prevista':datetime.datetime.now(),'justificacion':'Falta de stock','state':'open','picking_ids':[(6,0,pi)]})
            for r in requLin:
                r['req_rel']=requisicion.id
                self.env['product.rel.requisicion'].create(r)
            self.env['stock.picking'].browse(pi).write({'estado':'compras'})
            view = self.env.ref('studio_customization.default_form_view_fo_24cee64e-ad11-4f19-a7f6-fceca5375726')
            return {
                    'name': _('Transferencia'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'requisicion.requisicion',
                    #'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'current',
                    'res_id': requisicion.id,
                    'nodestroy': True
                    }
        else:
            return {'warning': {
            'title': _('Alerta'),
            'message': ('Las ordenes selcciondas tiene existencias o ya se encuntran con una requisicion.')
                    }}
class ProductAltaAction(TransientModel):
    _name = 'product.product.action'
    _description='Alta de referencias en masa'
    archivo=fields.Binary()
    almacen=fields.Many2one('stock.warehouse')

    def crear(self):
        if(self.archivo):
            f2=base64.b64decode(self.archivo)
            H=StringIO(f2)
            mimetype = guess_mimetype(f2 or b'')
            #_logger.info(str(mimetype))
            if(mimetype=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or mimetype=='application/vnd.ms-excel'):
                book = xlrd.open_workbook(file_contents=f2 or b'')
                sheet = book.sheet_by_index(0)
                header=[]
                arr=[]
                i=0
                j=0
                check=False
                for row_num, row in enumerate(sheet.get_rows()):
                    if(j>0):
                        if(row[2].ctype!=0):
                            if(row[2].value!=''):
                                if(int(row[2].value)>0):
                                    check=True
                    j=j+1
                id3=None
                if(check and self.almacen.id==False):
                    raise UserError(_("Se requiere almacen para cargar las existencias"))
                if(check and self.almacen.id!=False):
                    id3=self.env['stock.inventory'].create({'name':'Carga de creacion'+str(self.almacen.name), 'location_id':self.almacen.lot_stock_id.id,'x_studio_field_8gltH':self.almacen.id,'state':'done'})
                for row_num, row in enumerate(sheet.get_rows()):
                    if(i>0):
                        template=self.env['product.template'].search([('name','=',str(row[0].value).replace('.0','')),('categ_id', '=',13)])
                        productid=self.env['product.product'].search([('product_tmpl_id','=',template.id)])
                        unidad=self.env['uom.uom'].search([('name','=','Unidad(es)' if(row[3].value.lower()=='pieza') else row[3].value)])
                        producto=self.env['product.product'].search([['default_code','=',str(row[1].value).replace('.0','')]])
                        inventario=self.env['stock.quant'].search([['product_id','=',producto.id],['location_id','=',self.almacen.lot_stock_id.id]])
                        categoria=self.env['product.category'].search([['name','=',row[5].value]])
                        _logger.info(str(categoria.name))
                        if(producto.id==False):
                            producto=self.env['product.product'].create({'default_code':str(row[1].value).replace('.0',''),'categ_id':categoria.id,'x_studio_field_ry7nQ':productid.id,'description':row[4].value,'name':row[4].value,'uom_id':unidad.id if(unidad.id) else False})
                        if(check):
                            if(self.almacen):
                                quant={'product_id':producto.id,'reserved_quantity':'0','quantity':row[2].value, 'location_id':self.almacen.lot_stock_id.id}
                                inventoty={'inventory_id':id3.id, 'partner_id':'1','product_id':productid.id,'product_uom_id':'1','product_qty':row[2].value, 'location_id':self.almacen.lot_stock_id.id}
                                if(inventario.id):
                                    inventario.write({'quantity':row[2].value})
                                if(inventario.id==False):
                                    self.env['stock.quant'].sudo().create(quant)
                                self.env['stock.inventory.line'].create(inventoty)
                            else:
                                raise UserError(_("Se requiere almacen para cargar las existencias"))
                    i=i+1
            else:
                raise UserError(_("Archivo invalido"))
class  DevolverPick(TransientModel):
    _name='devolver.action'
    _description='devolucion a almacen'
    fecha=fields.Datetime()
    comentario=fields.Char()
    picking=fields.Many2one('stock.picking')

    def confirmar(self):
        pic=self.env['stock.picking'].search([['id','=',self.picking.id]])
        destino=None
        sale=self.env['sale.order'].search([['id','=',self.picking.sale_id.id]])
        ticket_id=sale.x_studio_field_bxHgp.id
        sale.write({'x_studio_field_bxHgp':False})
        s=sale.copy()
        s.write({'x_studio_field_bxHgp':ticket_id})
        sale.write({'x_studio_field_bxHgp':ticket_id})
        if(self.picking.picking_type_id.warehouse_id.id==1):
            destino=self.env['stock.picking.type'].search([['name','=','Recepciones'],['warehouse_id','=',self.picking.picking_type_id.warehouse_id.id]])
        if(self.picking.picking_type_id.warehouse_id.id!=1):
            destino=self.env['stock.picking.type'].search([['name','=','Receipts'],['warehouse_id','=',self.picking.picking_type_id.warehouse_id.id]])
        pick_origin1= self.env['stock.picking'].create({'picking_type_id' : destino.id,'almacenOrigen':self.picking.picking_type_id.warehouse_id.id,'almacenDestino':self.picking.picking_type_id.warehouse_id.id,'location_id':self.picking.location_id.id,'location_dest_id':self.picking.picking_type_id.warehouse_id.lot_stock_id.id})
        for l in self.picking.move_ids_without_package:
            datos1={'picking_id':pick_origin1.id,'product_id' : l.product_id.id, 'product_uom_qty' : l.product_uom_qty,'name':l.name if(l.product_id.description) else '/','product_uom':l.product_uom.id,'location_id':self.picking.location_id.id,'location_dest_id':self.picking.picking_type_id.warehouse_id.lot_stock_id.id}
            self.env['stock.move'].create(datos1)
        self.picking.action_cancel()
        pick_origin1.write({'x_studio_ticket':s.origin})
        pick_origin1.write({'partner_id':self.picking.partner_id.id})
        pick_origin1.write({'distribucion':True})
        pick_origin1.action_assign()
        pick_origin1.action_confirm()
        s.write({'x_studio_fecha_de_entrega':self.fecha,'commitment_date':self.fecha})
        self.env['helpdesk.diagnostico'].sudo().create({ 'ticketRelacion' : self.picking.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id, 'estadoTicket' : "Devuelto a Almacen", 'comentario':self.comentario}) 
        s.action_confirm()
        self.picking.x_studio_ticket_relacionado.write({'x_studio_field_0OAPP':[(4,s.id)]})
        
        
