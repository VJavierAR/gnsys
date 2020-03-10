from odoo import fields, api
from odoo.models import TransientModel
import logging, ast
import datetime, time
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
            quantities_done = sum(
                move_line.qty_done for move_line in
                assigned_picking_lst.mapped('move_line_ids').filtered(
                    lambda m: m.state not in ('done', 'cancel')))
            if not quantities_done:
                _logger.info("***************lista " + str(len(assigned_picking_lst)))
                CON=str(self.env['ir.sequence'].next_by_code('concentrado'))
                for l in assigned_picking_lst:
                    if(l.picking_type_id.id==3):
                        l.sudo().write({'concentrado':CON})
                        self.env['stock.picking'].search([['sale_id','=',l.sale_id.id]]).write({'concentrado':CON})
                return assigned_picking_lst.action_immediate_transfer_wizard()

            if assigned_picking_lst._check_backorder():
                #assigned_picking_lst.write({'backorder':''})
                return assigned_picking_lst.action_generate_backorder_wizard()
            assigned_picking_lst.sudo().action_done()
            data = {
                'ids': self.assigned_picking_lst,
                'model': self._name,
                #'form': {
                ##    'date_start': self.date_start,
                 #   'date_end': self.date_end,
                #},
            }
            return self.env.ref('stock_picking_mass_action.report_custom').report_action(self, data=data)
    @api.multi
    def test(self):
        do=[]
        for d in self.picking_ids:
            do.append(d.id)
        data = {
                #'docs':self.picking_ids,
                'model': 'stock.picking',
                #'form': {
                ##    'date_start': self.date_start,
                 #   'date_end': self.date_end,
                #},
            }
        return self.env.ref('stock_picking_mass_action.report_custom').report_action(self,data=data, config=True)


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
            for prp in self.pro_ids:
                if(prp.producto1.id !=prp.producto2.id):
                    dt.append(prp.producto1.id)
            for s in self.pick.sale_id.order_line:
                if(s.product_id.id in dt):
                    i=i+1
                    self.env.cr.execute("delete from stock_move_line where reference='"+self.pick.name+"' and product_id="+str(s.product_id.id)+";")
                    self.env.cr.execute("delete from stock_move where origin='"+self.pick.sale_id.name+"' and product_id="+str(s.product_id.id)+";")
                    self.env.cr.execute("delete from sale_order_line where id="+str(s.id)+" and product_id="+str(s.product_id.id)+";")
            if(i>0):
                _logger.info('hollaalal'+str(self.pick.sale_id.id))
                self.env.cr.execute("update stock_picking set state='draft' where sale_id="+str(self.pick.sale_id.id)+";")
                self.env.cr.execute("select id from stock_picking where sale_id="+str(self.pick.sale_id.id)+";")
                pickis=self.env.cr.fetchall()
                pickg=self.env['stock.picking'].search([['id','in',pickis]])
                for li in self.pro_ids:
                    datos={'order_id':self.pick.sale_id.id,'product_id':li.producto2.id,'product_uom':li.producto2.uom_id.id,'product_uom_qty':li.cantidad,'name':li.producto2.description if(li.producto2.description) else '/','price_unit':0.00,'x_studio_serieorderline':li.serie}
                    #if(li.serieDestino):
                    #    datos['x_studio_field_9nQhR']=li.serieDestino.id,
                    ss=self.env['sale.order.line'].sudo().create(datos)
                for p in pickg:
                    p.action_confirm()

class StockCambioLine(TransientModel):
    _name = 'cambio.toner.line'
    _description = 'Lineas cambio toner'
    producto1=fields.Many2one('product.product')
    producto2=fields.Many2one('product.product')
    cantidad=fields.Float()
    rel_cambio=fields.Many2one('cambio.toner')
    serie=fields.Char()