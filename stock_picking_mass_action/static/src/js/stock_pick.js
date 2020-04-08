
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
                this.$buttons.find('.oe_action_button').click(this.proxy('action_inter2'));
                this.$buttons.find('.oe_action_button_move_line').click(this.proxy('action_inter1'));
                this.$buttons.find('.oe_action_button_stock_quant').click(this.proxy('action_inter3'));
            }
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
                name: _t('Serie'),
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