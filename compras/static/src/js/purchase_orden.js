
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
                      default:
                        this.$buttons.find('.oe_action_button_purchase_report').click(this.proxy('action_inter8'));                     
                    }
                }
                
            }
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
    });
});