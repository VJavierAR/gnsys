
/*
function test() {
    console.log("Hola mundo");
    
    ///html/body/div[3]/div/div/div/div[5]/div[5]/h1/span
    var a=document.evaluate('/html/body/div[3]/div/div/div/div[5]/div[6]/table[1]/tbody/tr[19]/td[2]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.innerHTML;
    alert(a);
    //document.getElementsByClassName("o_field_char o_field_widget o_required_modifier field_name").style.color = "red";    
    
}
*/


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
                this.$buttons.find('.oe_action_button').click(this.proxy('action_def'));
            }
        },
/*
        action_def: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Crear ticket con base a una serie'),
                type : 'ir.actions.act_window',
                res_model: 'helpdesk.crearconserie',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_helpdesk_crear_desde_serie',
                views: [[false, 'form']],
                target: 'new',
            }, {
                on_reverse_breadcrumb: function () {
                    self.update_control_panel({clear: true, hidden: true});
                }
            });


            rpc.query({
                model: 'helpdesk.ticket',
                method: 'cambio_wizard',
                args: [[user],{'id':user}],
            });
        },*/

        /*receive_invoice: function () {
            var self = this
            var user = session.uid;
            rpc.query({
                model: 'helpdesk.ticket',
                method: 'cambio_wizard',
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
        },*/
    });

    /*
    var ListView = require('web.ListView');
    var QWeb = core.qweb;

    ListView.include({

        render_buttons: function($node) {
            var self = this;
            this._super($node);
                this.$buttons.find('.o_list_tender_button_create').click(this.proxy('tree_view_action'));
        },

        tree_view_action: function () {

            this.do_action({
                    type: "ir.actions.act_window",
                    name: "Series",
                    res_model: "helpdesk.ticket",
                    views: [[false,'form']],
                    target: 'current',
                    view_type : 'form',
                    view_mode : 'form',
                    flags: {'form': {'action_buttons': true, 'options': {'mode': 'edit'}}}
            });
            return { 'type': 'ir.actions.client'
                    ,'tag': 'reload', } 
        }
    });
    */
});


    $(document).ready(function() {
        console.log("Entrando al cargar...")
        //var x = document.getElementById("hidden_box");
        //var x=document.getElementsByClassName('blockUI blockMsg blockPage');
        //var y=document.getElementsByClassName('blockUI');
        //var z=document.getElementsByClassName('blockUI blockOverlay');

       
        var intervalo = setInterval( function borraBlock() {
                    var x=document.getElementsByClassName('blockUI blockMsg blockPage');
        var y=document.getElementsByClassName('blockUI');
        var z=document.getElementsByClassName('blockUI blockOverlay');
            console.log(x)
            if (x){
                x.parentNode.removeChild(x);
                y.parentNode.removeChild(y);
                z.parentNode.removeChild(z);
                        //document.body.removeChild(x);
        //document.body.removeChild(y);
        //document.body.removeChild(z);
        //i=x.remove();
        //j=y.remove();
        //k=z.remove();
            }
        }, 3000)
        
    });
