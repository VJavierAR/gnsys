
odoo.define('invoice.action_button', function (require) {
"use strict";

    var core = require('web.core');
    var ListController = require('web.ListController');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var _t = core._t;

    ListController.include({
        renderButtons: function($node) {
        this._super.apply(this, arguments);
            if (this.$buttons) {
                if (typeof this.actionViews !== 'undefined' && this.actionViews.length > 0) {
                    switch (this.actionViews[0].viewID) {
                      case 2940:
                        this.$buttons.find('.o_button_import').hide();
                        this.$buttons.find('.o_list_button_add').hide();
                        this.$buttons.find('.oe_action_button_ticket_report').click(this.proxy('action_inter5'));
                        break;
                      case 2941:
                        this.$buttons.find('.o_button_import').hide();
                        this.$buttons.find('.o_list_button_add').hide();
                        this.$buttons.find('.oe_action_button').click(this.proxy('action_inter2'));
                        break; 
                      case 646:
                        this.$buttons.find('.o_button_import').hide();
                        this.$buttons.find('.oe_action_button_stock_inventory').click(this.proxy('action_inter6'));
                        break;
                      default:
                        this.$buttons.find('.oe_action_button_sale_report').click(this.proxy('action_inter4')); 
                        this.$buttons.find('.oe_action_button_ticket_report').hide();
                        this.$buttons.find('.o_button_import').hide();
                        this.$buttons.find('.oe_action_button').hide();
                        this.$buttons.find('.oe_action_button_move_line').click(this.proxy('action_inter1'));
                        this.$buttons.find('.oe_action_button_product_product').click(this.proxy('action_inter7'));
                        this.$buttons.find('.oe_action_button_stock_quant').click(this.proxy('action_inter3'));
                        this.$buttons.find('.oe_action_button_purchase_order').click(this.proxy('action_inter8'));

                        
                    }
                }
                
            }
        },
        action_inter8: function (e) {
            var self = this
            var user = session.uid;
            var dataset = this.dataset;
            var active_id = dataset.ids[dataset.index]
            self.do_action({
                name: _t('Ordenes de Compra'),
                type : 'ir.actions.act_window',
                res_model: 'purchase.order.confirm',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'purchase_order_confirm_view',
                views: [[false, 'form']],
                target: 'new',
            
            });
        },

        
        action_inter7: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Inventario'),
                type : 'ir.actions.act_window',
                res_model: 'product.product.action',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_product_product_action_form',
                views: [[false, 'form']],
                target: 'new',
            
            });
        },
        action_inter6: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Inventario'),
                type : 'ir.actions.act_window',
                res_model: 'stock.inventory.action',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_stock_inventory_action_form',
                views: [[false, 'form']],
                target: 'new',
            
            });
        },
         action_inter5: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Tickets'),
                type : 'ir.actions.act_window',
                res_model: 'helpdesk.ticket.action',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_helpdesk_ticket_action_form',
                views: [[false, 'form']],
                target: 'new',
            
            });
        },
        action_inter4: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Solicitudes'),
                type : 'ir.actions.act_window',
                res_model: 'sale.order.action',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_sale_order_action_form',
                views: [[false, 'form']],
                target: 'new',
            
            });
        },
        action_inter3: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Existencias'),
                type : 'ir.actions.act_window',
                res_model: 'stock.quant.action',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_stock_quant_action_form',
                views: [[false, 'form']],
                target: 'new',
            
            });
        },


        action_inter2: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Transferencias Internas'),
                type : 'ir.actions.act_window',
                res_model: 'transferencia.interna',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_transferencia_interna',
                views: [[false, 'form']],
                target: 'new',
            }, {
                on_reverse_breadcrumb: function () {
                    self.update_control_panel({clear: true, hidden: true});
                }
            });


            rpc.query({
                model: 'stock.picking',
                method: 'inter_wizard',
                args: [[user],{'id':user}],
            });
        },
        action_inter1: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Movimientos'),
                type : 'ir.actions.act_window',
                res_model: 'stock.move.action',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_stock_move_action_form',
                views: [[false, 'form']],
                target: 'new',
            
            });
        },
        receive_invoice: function () {
            var self = this
            var user = session.uid;
            rpc.query({
                model: 'stock.picking',
                method: 'inter_wizard',
                args: [[user],{'id':user}],
                }).then(function (e) {
                    self.do_action({
                        name: _t('action_invoices'),
                        type: 'ir.actions.act_window',
                        res_model: 'name.name',
                        views: [[false, 'form']],
                        view_mode: 'form',
                        target: 'new',
                    });
                    window.location
                });
        },
    });
});