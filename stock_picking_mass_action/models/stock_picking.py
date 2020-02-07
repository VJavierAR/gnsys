from odoo import _, fields, api
from odoo.models import Model
import logging, ast
_logger = logging.getLogger(__name__)

class StockPicking(Model):
    _inherit = 'stock.picking'
    almacenOrigen=fields.Many2one('stock.warehouse','Almacen Origen')
    almacenDestino=fields.Many2one('stock.warehouse','Almacen Destino')
    hiden=fields.Integer(compute='hide')
    ajusta=fields.Boolean('Ajusta')
    #ticketOrigenEnVenta = fields.Char(string='Documento de origen en venta', store=True, related='sale_id.origin')
    estado = fields.Text(compute = 'x_historial_ticket_actualiza')
    lineTemp=fields.One2many('stock.pick.temp','picking')
    state = fields.Selection([
    ('draft', 'Draft'),('compras', 'Solicitud de Compra'),
    ('waiting', 'Waiting Another Operation'),
    ('confirmed', 'Sin Stock'),
    ('assigned', 'Por Validar'),
    ('done', 'Validado'),('distribucion', 'Distribución'),('cancel', 'Cancelled'),('aDistribucion', 'A Distribución')
], string='Status', compute='_compute_state',
    copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
    help=" * Draft: not confirmed yet and will not be scheduled until confirmed.\n"
         " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows).\n"
         " * Waiting: if it is not ready to be sent because the required products could not be reserved.\n"
         " * Ready: products are reserved and ready to be sent. If the shipping policy is 'As soon as possible' this happens as soon as anything is reserved.\n"
         " * Done: has been processed, can't be modified or cancelled anymore.\n"
         " * Cancelled: has been cancelled, can't be confirmed anymore.")
    """
    @api.onchange('carrier_tracking_ref')
    def agregarNumeroGuiaATicketOSolicitud(self):
        #Funcion que agrega numero de guia a ticket y refaccion
        ticketDeRefaccion = "Ticket de refacción"
        cadena = str(record.x_studio_documento_de_origen_en_venta)
        if ticketDeRefaccion in cadena:
            numeroDeGuia = str(self.carrier_tracking_ref)
            
        else:
            numeroDeGuia = str(self.carrier_tracking_ref)
            solicitudDeVenta = self.group_id
            solicitudDeVenta.env['sale.order'].sudo().write({'numeroDeGuiaDistribucion': numeroDeGuia})
            solicitudDeVenta.env['sale.order'].sudo().write({'comentarioDeDistribucion': self.x_studio_comentario})
    """
            
    
    
    @api.multi
    @api.depends('state')
    def x_historial_ticket_actualiza(self):
        _logger.info("********entro stock_picking.x_historial_ticket_actualiza()")
        for record in self:
            estadoActual = str(record.state)
            record['estado'] = estadoActual
            nombreStock = record.name
            #dis = "DIS"
            dis = "OUT"
            ticketDeRefaccion = "Ticket de refacción"
            ticketDeToner = "Ticket de tóner"
            cadena = str(record.x_studio_documento_de_origen_en_venta)
            
            if dis in nombreStock and (ticketDeRefaccion in cadena or ticketDeToner in cadena) and ('assigned' in estadoActual or 'done' in estadoActual) and self.env.user.id != 1:
                numTicket = cadena.split(': ')[1]
                #ticket = self.env['helpdesk.ticket'].search({'id': numTicket})
                #historialNotas = ticket.historialCuatro
                if 'assigned' in estadoActual:
                    _logger.info("********entro Refacción Para Entregar")
                    #existe = False
                    #for nota in historialNotas:
                    #    if str(nota.x_estado) == 'Refacción Para Entregar':
                    #        existe = True
                    #if existe == False:
                    self.env['x_historial_helpdesk'].sudo().create({ 'x_id_ticket' : numTicket
                                                                       , 'x_persona' : str(self.env.user.name)
                                                                       , 'x_estado' : "Refacción Para Entregar"
                                                                      })

                elif 'done' in estadoActual:
                    _logger.info("********entro Refacción Entregada")
                    #existe = False
                    #for nota in historialNotas:
                    #    if str(nota.x_estado) == 'Refacción Entregada':
                    #        existe = True
                    #if existe == False:
                    self.env['x_historial_helpdesk'].sudo().create({ 'x_id_ticket' : numTicket
                                                                       , 'x_persona' : str(self.env.user.name)
                                                                       , 'x_estado' : "Refacción Entregada"
                                                                      })
                    
    
    
    
    def action_toggle_is_locked(self):
        self.ensure_one()
        if(self.is_locked==True):
            #borrado
            self.lineTemp=[(5,0,0)]
            dat=[]
            for m in self.move_ids_without_package:
                dat.append({'producto':m.product_id.id,'cantidad':m.product_uom_qty,'ubicacion':self.location_id.id,'serieDestino':m.x_studio_serie_destino.id})
            self.sudo().lineTemp=dat
            for s in self.sale_id.order_line:
                self.env.cr.execute("delete from stock_move_line where reference='"+self.name+"';")
                self.env.cr.execute("delete from stock_move where origin='"+self.sale_id.name+"';")
                self.env.cr.execute("delete from sale_order_line where id="+str(s.id)+";")
        if(self.is_locked==False):
            self.env.cr.execute("update stock_picking set state='draft' where sale_id="+str(self.sale_id.id)+";")
            self.env.cr.execute("select id from stock_picking where sale_id="+str(self.sale_id.id)+";")
            pickis=self.env.cr.fetchall()
            pick=self.env['stock.picking'].search([['id','in',pickis]])
            for li in self.lineTemp:
                datos={'order_id':self.sale_id.id,'product_id':li.producto.id,'product_uom':li.producto.uom_id.id,'product_uom_qty':li.cantidad,'name':li.producto.description if(li.producto.description) else '/','price_unit':0.00}
                if(li.serieDestino):
                    datos['x_studio_field_9nQhR']=li.serieDestino.id,
                ss=self.env['sale.order.line'].sudo().create(datos)
            for p in pick:
                p.action_confirm()
        self.is_locked = not self.is_locked
        return True
    
    
    @api.depends('picking_type_id')
    def hide(self):
        for record in self:
            if(record.picking_type_id):
                if('internas' in record.picking_type_id.name or 'Internal' in record.picking_type_id.name):
                    record['hiden']=1
    
    @api.onchange('almacenOrigen')
    def cambioOrigen(self):
        self.location_id=self.almacenOrigen.lot_stock_id.id
    
    @api.onchange('almacenDestino')
    def cambioDestino(self):
        self.location_dest_id=self.almacenDestino.lot_stock_id.id
    
    
    @api.model
    def check_assign_all(self):
        """ Try to assign confirmed pickings """
        domain = [('picking_type_code', '=', 'outgoing'),
                  ('state', '=', 'confirmed')]
        records = self.search(domain, order='scheduled_date')
        records.action_assign()

    def action_immediate_transfer_wizard(self):
        view = self.env.ref('stock.view_immediate_transfer')
        wiz = self.env['stock.immediate.transfer'].create(
            {'pick_ids': [(4, p.id) for p in self]})
        return {
            'name': _('Immediate Transfer?'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.immediate.transfer',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }
class StockPicking(Model):
    _inherit = 'stock.move'
    almacenOrigen=fields.Many2one('stock.warehouse','Almacen Origen')
    
            
    @api.onchange('almacenOrigen')
    def cambioOrigen(self):
        if(self.almacenOrigen):
            self.location_id=self.almacenOrigen.lot_stock_id.id
        
class StockPickingMoveTemp(Model):
    _name='stock.pick.temp'
    _description='Lineas Temporales'
    producto=fields.Many2one('product.product')
    modelo=fields.Char(related='producto.name',string='Modelo')
    noParte=fields.Char(related='producto.default_code',string='No. Parte')
    descripcion=fields.Text(related='producto.description',string='Descripción')
    stock=fields.Many2one('stock.quant',string='Existencia')
    cantidad=fields.Integer('Demanda Inicial')
    almacen=fields.Many2one('stock.warehouse','Almacén Origen')
    ubicacion=fields.Many2one('stock.location','Ubicación')
    disponible=fields.Float(related='stock.quantity')
    picking=fields.Many2one('stock.picking')
    unidad=fields.Many2one('uom.uom',related='producto.uom_id')
    lock=fields.Boolean('lock')
    serieDestino=fields.Many2one('stock.production.lot')
    
    @api.onchange('ubicacion','producto')
    def quant(self):
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
