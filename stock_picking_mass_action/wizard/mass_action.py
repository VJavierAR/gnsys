from odoo import _,fields, api
from odoo.models import TransientModel
import logging, ast
import datetime, time
from odoo.tools.float_utils import float_compare
_logger = logging.getLogger(__name__)

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
            if(s.picking_type_id.id==3):
                check=2
            if(s.picking_type_id.id==29314):
                check=1
    @api.multi
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
                                datosr={'order_id' : sale.id, 'product_id' : rr.product_id.id, 'product_uom_qty' :rr.product_uom_qty,'x_studio_field_9nQhR':pick_id.x_studio_ticket_relacionado.x_studio_equipo_por_nmero_de_serie[0].id, 'price_unit': 0}
                                if(pick_id.x_studio_ticket_relacionado.team_id.id==10 or pick_id.x_studio_ticket_relacionado.team_id.id==11):
                                    datosr['route_id']=22548
                                self.env['sale.order.line'].create(datosr)
                            pick_id.x_studio_ticket_relacionado.write({'x_studio_field_0OAPP':[(4,sale.id)]})
                            sale.sudo().action_confirm()
                        backorder_pick.action_cancel()
            if(len(assigned_picking_lst2)>0):
                return self.env.ref('stock_picking_mass_action.report_custom').report_action(assigned_picking_lst2)
        return {'type': 'ir.actions.client','tag': 'reload'}


    @api.multi
    def vales(self):
        assigned_picking_lst2 = self.picking_ids.\
        filtered(lambda x: x.picking_type_id.id == 3 and x.state == 'done')
        return self.env.ref('stock.action_report_delivery').report_action(assigned_picking_lst2)
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
                        l=self.env['stock.production.lot'].search([['name','=',d[0]['serie']]])
                        datos={'x_studio_field_9nQhR':l.id,'order_id':self.pick.sale_id.id,'product_id':d[0]['producto2']['id'],'product_uom':d[0]['producto2']['uom_id']['id'],'product_uom_qty':d[0]['cantidad'],'name':d[0]['producto2']['description'] if(d[0]['producto2']['description']) else '/','price_unit':0.00}
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
    serie=fields.Char()
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



class ComemtarioTicket(TransientModel):
    _name = 'comentario.ticket'
    _description = 'Comemtario de Ticket'
    comentario=fields.Char(string='Comentario')
    evidencia=fields.Binary(string='Evidencia')
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
                                        ,'evidencia': [(4,self.evidencia)]
                                        ,'mostrarComentario': False
                                        })

class TransferInter(TransientModel):
    _name='transferencia.interna'
    _description='Transferencia Interna'    
    almacenOrigen=fields.Many2one('stock.warehouse','Almacen Origen')
    ubicacion=fields.Many2one(related='almacenOrigen.lot_stock_id')
    almacenDestino=fields.Many2one('stock.warehouse','Almacen Destino')
    lines=fields.One2many('transferencia.interna.temp','transfer')
    categoria=fields.Many2one('product.category','Categoria de productos')

    def confirmar(self):
        origen=self.env['stock.picking.type'].search([['name','=','Internal Transfers'],['warehouse_id','=',self.almacenOrigen.id]])
        destino=self.env['stock.picking.type'].search([['name','=','Internal Transfers'],['warehouse_id','=',self.almacenDestino.id]])

        pick_origin = self.env['stock.picking'].create({'picking_type_id' : origen.id, 'location_id':self.almacenOrigen.lot_stock_id.id,'location_dest_id':17})
        pick_dest = self.env['stock.picking'].create({'picking_type_id' : destino.id, 'location_id':17,'location_dest_id':self.almacenDestino.lot_stock_id.id})
        
        for l in self.lines:
            datos1={'product_id' : l.producto.id, 'product_uom_qty' : l.cantidad,'name':l.producto.description,'product_uom':l.unidad.id,'location_id':self.almacenOrigen.lot_stock_id.id,'location_dest_id':17}
            datos1['picking_id']= pick_origin.id
            datos2={'product_id' : l.producto.id, 'product_uom_qty' : l.cantidad,'name':l.producto.description,'product_uom':l.unidad.id,'location_id':17,'location_dest_id':self.almacenDestino.lot_stock_id.id}
            datos2['picking_id']= pick_dest.id
            self.env['stock.move'].create(datos1)
            self.env['stock.move'].create(datos2)
        pick_origin.action_confirm()
        pick_origin.action_assign()
        pick_dest.action_confirm()
        pick_dest.action_assign()
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
            'res_id': pick_origin.id,
            'nodestroy': True
        }




class TransferInterMoveTemp(TransientModel):
    _name='transferencia.interna.temp'
    _description='Lineas Temporales Transferencia'
    producto=fields.Many2one('product.product')
    modelo=fields.Char(related='producto.name',string='Modelo')
    noParte=fields.Char(related='producto.default_code',string='No. Parte')
    descripcion=fields.Text(related='producto.description',string='Descripción')
    stock=fields.Many2one('stock.quant',string='Existencia')
    cantidad=fields.Integer('Demanda Inicial')
    almacen=fields.Many2one('stock.warehouse','Almacén Origen')
    ubicacion=fields.Many2one('stock.location','Ubicación')
    disponible=fields.Float(related='stock.quantity',string='Disponible')
    transfer=fields.Many2one('transferencia.interna')
    unidad=fields.Many2one('uom.uom',related='producto.uom_id')
    categoria=fields.Many2one('product.category')

    #lock=fields.Boolean('lock')
    #serieDestino=fields.Many2one('stock.production.lot')
    
    @api.onchange('producto')
    def quant(self):
        if(self.producto):
            self.disponible=0
            h=self.env['stock.quant'].search([['product_id','=',self.producto.id],['location_id','=',self.ubicacion.id],['quantity','>',0]])
            if(len(h)>0):
                self.stock=h.id
            if(len(h)==0):
                d=self.env['stock.location'].search([['location_id','=',self.ubicacion.id]])
                for di in d:
                    i=self.env['stock.quant'].search([['product_id','=',self.producto.id],['location_id','=',di.id],['quantity','>',0]])
                    if(len(i)>0):
                        self.stock=i.id



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

    def report(self):
        if(self.almacen!=False and self.categoria!=False):
            d=self.env['stock.move.line'].search([['reference','like','IN']])
        if(self.categoria!=False and self.almacen==False):
            d=self.env['stock.move.line'].search([['reference','like','IN']])
        if(self.categoria==False and self.almacen!=False):
            d=self.env['stock.move.line'].search([['reference','like','IN']])
        else:
            d=self.env['stock.move.line'].search([['reference','like','IN']])

        return self.env.ref('stock_picking_mass_action.partner_xlsx').report_action(d)

