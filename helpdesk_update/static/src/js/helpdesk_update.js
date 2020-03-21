
/*
function test() {
    console.log("Hola mundo");
    
    ///html/body/div[3]/div/div/div/div[5]/div[5]/h1/span
    var a=document.evaluate('/html/body/div[3]/div/div/div/div[5]/div[6]/table[1]/tbody/tr[19]/td[2]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.innerHTML;
    alert(a);
    //document.getElementsByClassName("o_field_char o_field_widget o_required_modifier field_name").style.color = "red";    
    
}
*/



odoo.define('helpdesk_update.tree_view_button', function (require){
"use strict";

	var core = require('web.core');
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
});
