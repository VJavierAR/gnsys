
/*
function test() {
    console.log("Hola mundo");
    
    ///html/body/div[3]/div/div/div/div[5]/div[5]/h1/span
    var a=document.evaluate('/html/body/div[3]/div/div/div/div[5]/div[6]/table[1]/tbody/tr[19]/td[2]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.innerHTML;
    alert(a);
    //document.getElementsByClassName("o_field_char o_field_widget o_required_modifier field_name").style.color = "red";    
    
}
*/


odoo.define('invoice.action_button_helpdesk', function (require) {
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
				//console.log(this);
		    	//console.log(this.actionViews[0].viewID);
		    	if (this.actionViews[0].viewID == 2766) {
		    		this.$buttons.find('.o_button_import').hide();
		    		this.$buttons.find('.o_list_button_add').hide();
		    		this.$buttons.find('.oe_action_button_helpdesk').click(this.proxy('action_def'));
		    	} else {
		    		this.$buttons.find('.o_list_button_add').show();
		    		this.$buttons.find('.oe_action_button_helpdesk').hide();
		    	}
		    	//var div_blockUI = this.__parentedParent.el.lastElementChild.previousElementSibling.previousElementSibling
		    	//var div_blockUI_blockOverlay = this.__parentedParent.el.lastElementChild.previousElementSibling
		    	//var div_blockUI_blockMsg_blockPage = this.__parentedParent.el.lastElementChild
		    	/*
		    	if (this.__parentedParent.__parentedParent.el.lastElementChild.previousElementSibling.previousElementSibling.previousElementSibling != null){
			    	var div_blockUI = this.__parentedParent.__parentedParent.el.lastElementChild.previousElementSibling.previousElementSibling.previousElementSibling.previousSibling
			    	var div_blockUI_blockOverlay = this.__parentedParent.__parentedParent.el.lastElementChild.previousElementSibling.previousElementSibling.previousElementSibling
			    	var div_blockUI_blockMsg_blockPage = this.__parentedParent.__parentedParent.el.lastElementChild.previousElementSibling.previousElementSibling
			    	if (div_blockUI[0]) {
				    	div_blockUI.remove()
				    	div_blockUI_blockOverlay.remove()
				    	div_blockUI_blockMsg_blockPage.remove()
			    	}
			    }
			    */
		   	}
		},

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
        },

        receive_invoice: function () {
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
        },
	});

    $(document).ready(function() {
        console.log("Entrando al cargar...")
        //var x = document.getElementById("hidden_box");
        var x = $('.blockUI blockOverlay');
        console.log(x)

        function borraBlock() {
            var x = $('.blockUI blockOverlay');
            console.log(x)
            if ($(".blockUI blockOverlay")[0]){
                $('.blockUI blockOverlay').remove();
            }
        }
        //var intervalo = setInterval("borraBlock()", 3000)
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