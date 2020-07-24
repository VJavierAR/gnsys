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
    tecnicos=fields.One2many('mass.tecnico','mass_id')

    @api.depends('picking_ids')
    def che(self):
        for s in self.picking_ids:
            #Almacen
            if(s.picking_type_id.id==3 or s.picking_type_id.id==31485):
                self.check=2
            #refacion
            if(s.picking_type_id.id==29314):
                self.tecnicos=[{'pick_id':s.id}]
                #self.env['mass.tecnico'].create({'mass_id':self.id,'pick_id':s.id})
                self.check=1
            #ruta
            if(s.picking_type_id.id==2):
                self.check=3
            #distribucion
            if(s.picking_type_id.id==29302):
                self.check=4

    #@api.onchange('check')
    #def massTecnicoSSSS(self):
    #    if(self.check==1):
    #        for picki in self.picking_ids:
    #            self.env['mass.tecnico'].create({'mass_id':self.id,'pick_id':picki.id})

    def mass_action(self):
        self.ensure_one()
        draft_picking_lst = self.picking_ids.filtered(lambda x: x.state == 'draft').sorted(key=lambda r: r.scheduled_date)
        draft_picking_lst.sudo().action_confirm()
        pickings_to_check = self.picking_ids.filtered(lambda x: x.state not in ['draft','cancel','done',]).sorted(key=lambda r: r.scheduled_date)
        pickings_to_check.sudo().action_assign()
        cantidad=self.picking_ids.mapped('sale_id.delivery_count')
        loca=self.picking_ids.mapped('sale_id.warehouse_id.lot_stock_id.id')
        assigned_picking_lst = self.picking_ids.filtered(lambda x: x.state == 'assigned').sorted(key=lambda r: r.scheduled_date)
        assigned_picking_lst2 = self.picking_ids.filtered(lambda x:(loca[0] ==x.location_id.id and x.state == 'assigned' and  1 not in cantidad) or (x.state == 'assigned' and  1 in cantidad) )
        quantities_done = sum(move_line.qty_done for move_line in assigned_picking_lst.mapped('move_line_ids').filtered(lambda m: m.state not in ('done', 'cancel')))
        validacion=assigned_picking_lst.mapped('picking_type_id.id')
        tipo=assigned_picking_lst.mapped('picking_type_id.code')
        _logger.info(str(tipo))
        if(self.check ==2 or self.check ==1):
            CON=str(self.env['ir.sequence'].next_by_code('concentrado'))
            self.env['stock.picking'].search([['sale_id','in',assigned_picking_lst.mapped('sale_id.id')]]).write({'concentrado':CON})
            resto=assigned_picking_lst.filtered(lambda x:x.sale_id.id==False)
            for r in resto:
                self.env['stock.picking'].search([['origin','=',r.origin]]).write({'concentrado':CON})        
        pick_to_backorder = self.env['stock.picking']
        pick_to_do = self.env['stock.picking']
        for picking in assigned_picking_lst:
            for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                for move_line in move.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty
            if picking._check_backorder():
                pick_to_backorder |= picking
                continue
            if(picking.sale_id.x_studio_field_bxHgp):
                if(self.check==2):
                    picking.sale_id.x_studio_field_bxHgp.write({'stage_id':94})
                    self.env['helpdesk.diagnostico'].sudo().create({ 'ticketRelacion' : picking.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id, 'estadoTicket' : "A distribución", 'comentario':''}) 
                if(self.check==3):
                    if picking._check_backorder():
                        picking.sale_id.x_studio_field_bxHgp.write({'stage_id':109})
                        self.env['helpdesk.diagnostico'].sudo().create({ 'ticketRelacion' : picking.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id, 'estadoTicket' : "Entregado", 'comentario':picking.x_studio_comentario_1+' Evidenciado'})                        
                    else:
                        picking.sale_id.x_studio_field_bxHgp.write({'stage_id':18})
                        self.env['helpdesk.diagnostico'].sudo().create({ 'ticketRelacion' : picking.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id, 'estadoTicket' : "Entregado", 'comentario':picking.x_studio_comentario_1+' Evidenciado'})    
                if(self.check==4):
                    picking.sale_id.x_studio_field_bxHgp.write({'stage_id':94})
                    self.env['helpdesk.diagnostico'].sudo().create({ 'ticketRelacion' : picking.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id, 'estadoTicket' : "Distribución", 'comentario':''}) 
                if(self.check==1):
                    if(picking.location_dest_id.id!=16):
                        picking.sale_id.x_studio_field_bxHgp.write({'stage_id':104})
                        self.env['helpdesk.diagnostico'].sudo().create({ 'ticketRelacion' : picking.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id, 'estadoTicket' : "Entregado", 'comentario':picking.x_studio_comentario_1+' Evidenciado'})
                    else:
                        picking.sale_id.x_studio_field_bxHgp.write({'stage_id':18})
                        self.env['helpdesk.diagnostico'].sudo().create({ 'ticketRelacion' : picking.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id, 'estadoTicket' : "Entregado", 'comentario':picking.x_studio_comentario_1+' Evidenciado'})    
            pick_to_do |= picking
        if pick_to_do:
            pick_to_do.action_done()
        if pick_to_backorder and assigned_picking_lst.mapped('sale_id.id')==[]:
            pick_to_backorder.action_done()
        self.picking_ids.action_done()
        if(len(assigned_picking_lst2)>0):
            return self.env.ref('stock_picking_mass_action.report_custom').report_action(assigned_picking_lst2)
        for pp in assigned_picking_lst.filtered(lambda x:x.sale_id.x_studio_tipo_de_solicitud!="Retiro" and x.sale_id.x_studio_field_bxHgp==False):
            if('incoming' not in tipo):
                if('outgoing' in tipo):
                    if(pp.sale_id.x_studio_requiere_instalacin==True):
                        self.env['helpdesk.ticket'].create({'x_studio_tipo_de_vale':'Instalación','partner_id':pp.partner_id.parent_id.id,'x_studio_empresas_relacionadas':pp.partner_id.id,'team_id':9,'diagnosticos':[(0,0,{'estadoTicket':'Abierto','comentario':'Instalacion de Equipo'})],'stage_id':89,'name':'Instalaccion '+'Serie: '})                
                else:
                    move_lines=self.env['stock.move.line'].search([['move_id','in',pp.mapped('move_lines.id')]])
                    tipo2=move_lines.mapped('move_id.picking_type_id.name')
                    if('Surtir' in tipo2):
                        move_lines.lot_id.write({'x_studio_etapa':'A Distribución'})
                    if('Distribución' in tipo2):
                      record.lot_id.write({'x_studio_etapa':'Tránsito'})
                    if('Tránsito' in tipo2):
                      record.lot_id.write({'x_studio_etapa':'Ruta'})
        if(self.check==1):
            for t in self.tecnicos:
                _logger.info('tecnico'+t.tecnico.id+'pic'+t.pick_id.id)
                t.pick_id.write({'x_studio_tecnico':t.tecnico.id})

    @api.multi
    def vales(self):
        assigned_picking_lst2 = self.picking_ids.\
        filtered(lambda x: x.picking_type_id.id == 3 and x.state == 'done')
        if(assigned_picking_lst2.mapped('sale_id.id')==[]):
            return self.env.ref('stock.action_report_picking').report_action(assigned_picking_lst2)
        else:
            return self.env.ref('studio_customization.vale_de_entrega_56cdb2f0-51e3-447e-8a67-6e5c7a6b3af9').report_action(assigned_picking_lst2)      
    @api.multi
    def etiquetas(self):
        assigned_picking_lst2 = self.picking_ids.\
        filtered(lambda x: x.picking_type_id.id == 3 and x.state == 'done')
        return self.env.ref('studio_customization.transferir_reporte_4541ad13-9ccb-4a0f-9758-822064db7c9a').report_action(assigned_picking_lst2)
class MassActionTecnico(TransientModel):
    _name='mass.tecnico'
    _description='Listado para tecnicos'
    mass_id=fields.Many2one('stock.picking.mass.action')
    pick_id=fields.Many2one('stock.picking')
    tecnico=fields.Many2one('hr.employee')
    origin=fields.Char(related='pick_id.origin')
    partner_id=fields.Many2one(related='pick_id.partner_id')
    scheduled_date=fields.Datetime(related='pick_id.scheduled_date')
    x_studio_toneres=fields.Char(related='pick_id.x_studio_toneres')

    #@api.depends('tecnico')
    #def escribeTecnico(self):
    #    for record in self:
    #        if(record.tecnico):
    #            record.pick_id.write({'x_studio_tecnico':record.tecnico.id})



class StockIngreso(TransientModel):
    _name='ingreso.almacen'
    _description='Ingreso Almacen'
    pick=fields.Many2one('stock.picking')
    move_line=fields.One2many('ingreso.lines','rel_ingreso')
    almacen=fields.Many2one('stock.warehouse','Almacen')
    def confirmar(self):
        self.pick.write({'location_dest_id':self.almacen.lot_stock_id.id})
        for m in self.move_line:
            m.write({'location_dest_id':self.almacen.lot_stock_id.id})
            l=self.env['stock.move.line'].search([['move_id','=',m.move.id]])
            l.write({'location_dest_id':self.almacen.lot_stock_id.id,'qty_done':m.cantidad})
            if(m.producto.id!=m.producto2.id):
                l.write({'state':'draft'})
                l.write({'product_id':m.producto2.id})
                l.write({'state':'assigned'})
        self.pick.purchase_id.write({'recibido':'recibido'})
        self.env['stock.picking'].search([['state','=','assigned']]).action_assign()
        self.pick.action_done()
        return self.env.ref('stock.action_report_picking').report_action(self.pick)

class StockIngresoLines(TransientModel):
    _name='ingreso.lines'
    _description='lineas de ingreso'
    rel_ingreso=fields.Many2one('ingreso.almacen')
    producto=fields.Many2one('product.product')
    producto2=fields.Many2one('product.product')
    cantidad=fields.Integer()
    move=fields.Many2one('stock.move')    



class StockCambio(TransientModel):
    _name = 'cambio.toner'
    _description = 'Cambio toner'
    pick=fields.Many2one('stock.picking')
    pro_ids = fields.One2many('cambio.toner.line','rel_cambio')
    tonerUorden=fields.Boolean()
    toner_ids = fields.One2many('cambio.toner.line.toner','rel_cambio')
    accesorios_ids = fields.One2many('cambio.toner.line.accesorios','rel_cambio')



    def otra(self):
        equipos=self.pro_ids.filtered(lambda x:x.producto1.categ_id.id==13)
        if(len(equipos)==0):
            self.confirmar(self.pro_ids)
        else:   
            self.confirmar(self.accesorios_ids)
            self.confirmar(self.toner_ids)
            self.confirmarE(equipos)
            #self.confirmar()
        self.pick.action_confirm()
        self.pick.action_assign()


    def confirmar(self,data):
        if(self.pick.sale_id):
            i=0
            self.pick.backorder=''
            dt=[]
            al=[]
            for sa in self.pick.move_ids_without_package.filtered(lambda x:x.product_id.categ_id.id!=13):
                copia=sa.location_dest_id.id
                d=list(filter(lambda x:x['producto1']['id']==sa.product_id.id,data))
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
                        self.env['stock.move'].search([['picking_id.sale_id','=',self.pick.sale_id.id],['product_id','=',d[0]['producto2']['id']]]).write({'location_id':d[0]['almacen']['lot_stock_id']['id'],'location_dest_id':copia})
                    else:
                        if(d[0]['almacen']['id']):
                            self.env['stock.move'].search([['origin','=',str(self.pick.sale_id.name)],['product_id','=',d[0]['producto2']['id']]]).write({'location_dest_id':copia,'location_id':d[0]['almacen']['lot_stock_id']['id']})







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
    def confirmarE(self,equipos):
        for s in equipos:
            d=self.env['stock.move.line'].search([['move_id','=',s.move_id.id]])
            d.write({'lot_id':s.serieOrigen.id})

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
   
    serieOrigen=fields.Many2one('stock.production.lot',domain="['&',('product_id.id','=',producto1),('x_studio_estado','=',estado)]")
    estado=fields.Selection([["Obsoleto","Obsoleto"],["Usado","Usado"],["Hueso","Hueso"],["Para reparación","Para reparación"],["Nuevo","Nuevo"],["Buenas condiciones","Buenas condiciones"],["Excelentes condiciones","Excelentes condiciones"],["Back-up","Back-up"],["Dañado","Dañado"]])
    #modelo=fields.Many2one(related='serieOrigen.product_id')
    color=fields.Selection(related='producto1.x_studio_color_bn')
    contadorMono=fields.Integer('Contador Monocromatico')
    contadorColor=fields.Integer('Contador Color')
    move_id=fields.Many2one('stock.move')
    categoria=fields.Integer(related='producto1.categ_id.id')
    nivelNegro=fields.Float()
    nivelCian=fields.Float()
    nivelAmarillo=fields.Float()
    nivelMagenta=fields.Float()

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
    
    @api.onchange('almacen','estado')
    def filtroEqui(self):
        res={}
        ubicacion=0
        if(self.producto1.categ_id.id==13):
            series=[]
            ubicacion=self.move_id.location_id.id
            if(self.almacen):
                ubicacion=self.almacen.lot_stock_id.id
            existencias=self.env['stock.quant'].search([['location_id','=',ubicacion],['product_id','=',self.producto1.id]]).mapped('lot_id.id')
            if(len(existencias)>1):
                series=self.env['stock.production.lot'].search([['id','in',existencias]])
            if(self.estado):
                if(series!=[]):
                    series=series.filtered(lambda x:x.x_studio_estado==self.estado)
                else:
                    series=self.env['stock.production.lot'].search([['x_studio_estado','=',self.estado],['product_id','=',self.producto1.id],['id','in',existencias]])
            res['domain']={'serieOrigen':[['id','in',series.mapped('id')]]}
        return res

class StockCambioLine(TransientModel):
    _name = 'cambio.toner.line.toner'
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
    move_id=fields.Many2one('stock.move')
    #modelo=fields.Char(related='move_id.x_studio_modelo')
    
    @api.depends('almacen')
    def almac(self):
        for record in self:
            if(record.almacen):
                ex=self.env['stock.quant'].search([['location_id','=',record.almacen.lot_stock_id.id],['product_id','=',record.producto1.id]]).sorted(key='quantity',reverse=True)
                record.existeciaAlmacen=int(ex[0].quantity) if(len(ex)>0) else 0

class StockCambioLine(TransientModel):
    _name = 'cambio.toner.line.accesorios'
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
    move_id=fields.Many2one('stock.move')
    #modelo=fields.Char(related='move_id.x_studio_modelo')

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
        if(5>len(self.comentario)):
            raise UserError(_("Ingresar un comentario más extenso"))
        if(self.ruta==False):
            self.pick.x_studio_evidencia_a_ticket=self.evidencia
            self.pick.x_studio_comentario_1=self.comentario
            self.env['helpdesk.diagnostico'].sudo().create({ 'ticketRelacion' : self.pick.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id, 'estadoTicket' : "Devuelto a Distribución", 'comentario':self.comentario}) 
        if(self.ruta!=False and self.pick.sale_id.id!=False):
            self.pick.x_studio_evidencia_a_ticket=self.evidencia
            self.pick.x_studio_comentario_1=self.comentario
            self.env['helpdesk.diagnostico'].create({'ticketRelacion': self.pick.sale_id.x_studio_field_bxHgp.id
                                        ,'comentario': self.comentario
                                        ,'estadoTicket': self.pick.sale_id.x_studio_field_bxHgp.stage_id.name
                                        ,'evidencia': [(6,0,self.evidencia.ids)]
                                        ,'mostrarComentario': False
                                        })
            if(len(self.evidencia)==0 and self.pick.ruta_id.tipo!="foraneo"):
                raise UserError(_("Falta evidencia"))
            else:
                wiz=self.env['stock.picking.mass.action'].create({'picking_ids':[(4,self.pick.id)],'confirm':True,'check_availability':True,'transfer':True})
                wiz.mass_action()
        if(self.ruta!=False and self.pick.sale_id.id==False):
            if(len(self.evidencia)==0 and self.pick.ruta_id.tipo!="foraneo"):
                raise UserError(_("Falta evidencia"))
            else:
                wiz=self.env['stock.picking.mass.action'].create({'picking_ids':[(4,self.pick.id)],'confirm':True,'check_availability':True,'transfer':True})
                wiz.mass_action()


class TransferInter(TransientModel):
    _name='transferencia.interna'
    _description='Transferencia Interna'    
    almacenPadre=fields.Many2one('stock.warehouse','Almacen Padre')
    almacenOrigen=fields.Many2one('stock.warehouse','Almacen Hijo',domain="[('x_studio_almacn_padre','=',almacenPadre)]")
    ubicacion=fields.Many2one(related='almacenOrigen.lot_stock_id')
    almacenDestino=fields.Many2one('stock.warehouse','Almacen Destino')
    lines=fields.One2many('transferencia.interna.temp','transfer')
    categoria=fields.Many2one('product.category','Categoria de productos')
    archivo=fields.Binary()
    
    @api.onchange('archivo')
    def agregarLineas(self):
        if(self.archivo):
            f2=base64.b64decode(self.archivo)
            H=StringIO(f2)
            mimetype = guess_mimetype(f2 or b'')
            if(mimetype=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
                book = xlrd.open_workbook(file_contents=f2 or b'')
                sheet = book.sheet_by_index(0)
                header=[]
                arr=[]
                i=0
                for row_num, row in enumerate(sheet.get_rows()):
                    if(i>0):
                        code=str(row[1].value).split('0',1)[0].replace('.0','') if(str(row[1].value)[0]=='0') else str(row[1].value).replace('.0','')
                        p=self.env['product.product'].search([['default_code','=',code]])
                        self.lines=[{'producto':p.id,'cantidad':int(row[2].value)}]
                    i=i+1
                    

    def confirmar(self):
        pick_dest=[]
        pick_origin=[]
        pick_origin1=[]
        pick_origin2=[]
        pick_origin3=[]
        cliente=self.env['res.partner'].search([['name','=',self.almacenDestino.name],['parent_id','=',1]])
        oden=self.env['sale.order'].create({'partner_id':cliente.id,'partner_shipping_id':cliente.id})
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
                pick_origin1= self.env['stock.picking'].create({'partner_id':cliente.id,'origin':oden.name,'internas':True,'picking_type_id' : origen1.id,'almacenOrigen':self.almacenOrigen.id,'almacenDestino':self.almacenDestino.id,'location_id':origen1.default_location_src_id.id,'location_dest_id':origen2.default_location_src_id.id})
                pick_origin2= self.env['stock.picking'].create({'partner_id':cliente.id,'origin':oden.name,'internas':True,'picking_type_id' : origen2.id,'almacenOrigen':self.almacenOrigen.id,'almacenDestino':self.almacenDestino.id,'location_id':origen2.default_location_src_id.id,'location_dest_id':origen3.default_location_src_id.id})
                pick_origin3= self.env['stock.picking'].create({'partner_id':cliente.id,'origin':oden.name,'internas':True,'picking_type_id' : origen3.id,'almacenOrigen':self.almacenOrigen.id,'almacenDestino':self.almacenDestino.id,'location_id':origen3.default_location_src_id.id,'location_dest_id':17})
                pick_dest = self.env['stock.picking'].create({'partner_id':cliente.id,'origin':oden.name,'internas':True,'picking_type_id' : destino.id, 'location_id':17,'almacenOrigen':self.almacenOrigen.id,'almacenDestino':self.almacenDestino.id,'location_dest_id':self.almacenDestino.lot_stock_id.id})
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
            d.append(['location_id','in',self.almacen.mapped('lot_stock_id.id')])
        if(self.categoria):
            d.append(['x_studio_categoria','=',self.categoria.id])
            if(self.categoria.id==13):
                d.append(['x_studio_almacn.x_studio_cliente','=',False])
                if(self.almacen):
                    d.append(['location_id','in',self.almacen.mapped('lot_stock_id.id')])
                if(len(self.almacen)==0):
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
        d=self.env['sale.order'].search(i,order='confirmation_date asc').filtered(lambda x:x.origin==False and x.x_studio_factura==False)
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
    fechaauto=fields.Boolean('Fecha Automatica',default=True)

    @api.onchange('fechaauto')
    def automatica(self):
        if(self.fechaauto==True):
            fecha=datetime.datetime.now()
            fecha2=fecha-datetime.timedelta(days=90)
            self.fechaInicial=fecha2
            self.fechaFinal=fecha



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
                        print(row[1].value)
                        ubicacion=None
                        template=self.env['product.template'].search([('default_code','=',str(row[1].value).replace('.0',''))]).sorted(key='id',reverse=True)
                        productid=self.env['product.product'].search([('product_tmpl_id','=',template[0].id if(len(template)>1) else template.id)])
                        if(productid.id==False):
                            productid=self.env['product.product'].create({'name':row[0].value,'default_code':row[1].value,'description':row[4].value})
                        quant={'product_id':productid.id,'reserved_quantity':'0','quantity':row[2].value, 'location_id':self.almacen.lot_stock_id.id}
                        inventoty={'inventory_id':id3.id, 'partner_id':'1','product_id':productid.id,'product_uom_id':'1','product_qty':row[2].value, 'location_id':self.almacen.lot_stock_id.id}
                        if(row[3].ctype!=0 and row[3].value!=''):
                            ubicacion=self.env['x_ubicacion_inventario'].search([('x_name','=',str(row[3].value).replace('.0',''))])
                            if(len(ubicacion)==0):
                                ubicacion=self.env['x_ubicacion_inventario'].create({'x_name':str(row[3].value).replace('.0','')})
                        if(ubicacion!=None):
                            inventoty['x_studio_field_yVDjd']=ubicacion.id
                        _logger.info(str(row[1].value))
                        self.env['stock.inventory.line'].create(inventoty)
                        busqueda=self.env['stock.quant'].search([['product_id','=',productid.id],['location_id','=',self.almacen.lot_stock_id.id]])
                        _logger.info(str(busqueda))
                        if(len(busqueda)>0):
                            jj=0
                            if(len(busqueda)>1):
                                for b in busqueda:
                                    if(jj>0):
                                        b.unlink()
                                    jj=jj+1
                            if(ubicacion!=None):
                                busqueda[0].sudo().write({'quantity':row[2].value,'x_studio_field_kUc4x':ubicacion.id})                            
                            else:
                                busqueda[0].sudo().write({'quantity':row[2].value})
                        if(len(busqueda)==0):
                            if(ubicacion!=None):
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
            #pppp=self.env['stock.picking'].browse(pi).write({'estado':'compras'})
            for pp in self.picking_ids:
                pp.x_studio_ticket_relacionado.write({'stage_id':113})
                self.env['helpdesk.diagnostico'].sudo().create({ 'ticketRelacion' : pp.x_studio_ticket_relacionado.id, 'estadoTicket' : "Pendiente de compra", 'comentario':"Pendiente de compra Requisicion:("+requisicion.name+")"}) 
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
                            producto=self.env['product.product'].create({'default_code':str(row[1].value).replace('.0',''),'categ_id':categoria.id,'x_studio_field_ry7nQ':productid.id,'description':row[4].value,'name':row[0].value,'uom_id':unidad.id if(unidad.id) else False})
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
    tipo=fields.Selection([["Total","Total"],["Parcial","Parcial"]])

    def confirmar(self):
        pic=self.env['stock.picking'].search([['id','=',self.picking.id]])
        destino=None
        sale=self.env['sale.order'].search([['id','=',self.picking.sale_id.id]])
        ticket_id=sale.x_studio_field_bxHgp.id
        if(self.picking.picking_type_id.warehouse_id.id==1):
            destino=self.env['stock.picking.type'].search([['name','=','Recepciones'],['warehouse_id','=',self.picking.picking_type_id.warehouse_id.id]])
        if(self.picking.picking_type_id.warehouse_id.id!=1):
            destino=self.env['stock.picking.type'].search([['name','=','Receipts'],['warehouse_id','=',self.picking.picking_type_id.warehouse_id.id]])
        pick_origin1= self.env['stock.picking'].create({'picking_type_id' : destino.id,'almacenOrigen':self.picking.picking_type_id.warehouse_id.id,'almacenDestino':self.picking.picking_type_id.warehouse_id.id,'location_id':self.picking.location_id.id,'location_dest_id':self.picking.picking_type_id.warehouse_id.lot_stock_id.id})
        for l in self.picking.move_ids_without_package:
            datos1={'picking_id':pick_origin1.id,'product_id' : l.product_id.id, 'product_uom_qty' : l.product_uom_qty,'name':l.name if(l.product_id.description) else '/','product_uom':l.product_uom.id,'location_id':self.picking.location_id.id,'location_dest_id':self.picking.picking_type_id.warehouse_id.lot_stock_id.id}
            self.env['stock.move'].create(datos1)
        self.picking.action_cancel()
        pick_origin1.write({'x_studio_ticket':sale.origin})
        pick_origin1.write({'partner_id':self.picking.partner_id.id})
        pick_origin1.write({'distribucion':True})
        pick_origin1.action_assign()
        pick_origin1.action_confirm()
        if(self.tipo=="Parcial"):
            sale.write({'x_studio_field_bxHgp':False})
            s=sale.copy()
            s.write({'x_studio_field_bxHgp':ticket_id})
            sale.write({'x_studio_field_bxHgp':ticket_id})
            s.write({'x_studio_fecha_de_entrega':self.fecha,'commitment_date':self.fecha})
            s.action_confirm()
            self.picking.x_studio_ticket_relacionado.write({'x_studio_field_0OAPP':[(4,s.id)]})
        self.env['helpdesk.diagnostico'].sudo().create({ 'ticketRelacion' : self.picking.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id, 'estadoTicket' : "Devuelto a Almacen", 'comentario':self.comentario}) 
        
class StockQua(TransientModel):
    _name='quant.action'
    _description='Ajuste en quant'
    quant=fields.Many2one('stock.quant')
    producto=fields.Many2one('product.product')
    cantidad=fields.Float()
    ubicacion=fields.Many2one('x_ubicacion_inventario')
    comentario=fields.Char()
    usuario=fields.Many2one('res.users')

    def confirmar(self):
        self.env['stock.quant.line'].sudo().create({'quant_id':self.quant.id,'descripcion':self.comentario,'cantidadAnterior':self.quant.quantity,'cantidadReal':self.cantidad,'usuario':self.usuario.id})
        self.quant.sudo().write({'quantity':self.cantidad,'x_studio_field_kUc4x':self.ubicacion.id})
        self.env['stock.picking'].search([['state','=','confirmed']]).action_assign()

class SerieIngreso(TransientModel):
    _name='serie.ingreso'
    _description='Ingreso desde proveedor'
    picking=fields.Many2one('stock.picking')
    lineas=fields.One2many('serie.ingreso.line','serie_rel')
    almacen=fields.Many2one('stock.warehouse','Almacen')
    archivo=fields.Binary('Archivo')

    def confirmar(self):
        for mv in self.lineas:
            mv.write({'location_dest_id':self.almacen.lot_stock_id.id})
            mv.move_line.write({'location_dest_id':self.almacen.lot_stock_id.id,'lot_id':mv.serie.id,'qty_done':mv.cantidad})
        #if(len(self.lineas.mapped('serie.id'))!=len(self.lineas)):
        #    raise UserError(_("Faltan serie por ingresar"))   
        if(len(self.lineas.mapped('serie.id'))==len(self.lineas)):
            self.picking.action_done()
        self.picking.purchase_id.write({'recibido':'recibido'})
        self.env['stock.picking'].search([['state','=','assigned']]).action_assign()
        return self.env.ref('stock.action_report_picking').report_action(self.picking)



class SerieIngresoLine(TransientModel):
    _name='serie.ingreso.line'
    _description='Lineas de ingreso equipos'
    producto=fields.Many2one('product.product','Modelo')
    cantidad=fields.Float('Cantidad')
    serie=fields.Many2one('stock.production.lot')
    serie_rel=fields.Many2one('serie.ingreso')
    move_line=fields.Many2one('stock.move.line')


class AddCompatibles(TransientModel):
    _name='add.compatible'
    _description='Agregar Compatibles'
    productoInicial=fields.Many2one('product.product')
    productoCompatible=fields.Many2one('product.product')

    def confirmar(self):
        self.productoInicial.write({'x_studio_toner_compatible':[(4,self.productoCompatible.id)]})

class ReporteCompras(TransientModel):
    _name='purchase.order.action'
    _description='Reporte de compras'
    fechaInicial=fields.Datetime()
    fechaFinal=fields.Datetime()
    tipo=fields.Selection([["Pagos","Pagos"],["Compras","Compras"]])
    usuario=fields.Selection([["Claudia Moreno","Claudia Moreno"],["Veronica Aparicio","Veronica Aparicio"]])

    def report(self):
        i=[]
        d=[]
        j=[]
        if(self.fechaInicial):
            m=['date_planned','>=',self.fechaInicial]
            i.append(m)
        if(self.fechaFinal):
            m=['date_planned','<=',self.fechaFinal]
            i.append(m)
        if(self.usuario=="Claudia Moreno"):
            m=['x_studio_claudia','=',True]
            i.append(m)
        if(self.usuario=="Veronica Aparicio"):
            m=['x_studio_vernica','=',True]
            i.append(m)
        if(self.tipo=="Pagos"):
            m=['x_studio_impuesto','!=',0]
            i.append(m)
        if(self.tipo=="Compras"):
            i.append(['state','=','purchase'])    
        d=self.env['purchase.order'].search(i,order='date_planned asc')
        d[0].write({'x_studio_arreglo':str(d.mapped('id'))})
        return self.env.ref('stock_picking_mass_action.compras_xlsx').report_action(d[0])