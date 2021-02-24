
odoo.define('invoice.action_button_ticket_reporte', function (require) {
    "use strict";
        console.log("Entro al de gastos 444")
        
        var core = require('web.core');
        var ListController = require('web.ListController');
        var rpc = require('web.rpc');
        var session = require('web.session');
        var _t = core._t;
    
    
        ListController.include({
            renderButtons: function($node) {
            this._super.apply(this, arguments);
                //console.log($node)
                //console.log(this)
                //console.log(arguments)
                if (this.$buttons) {
                    //console.log(this);
                    //console.log("Test: " + this.actionViews[0].viewID);
                    if (typeof this.actionViews !== 'undefined' && this.actionViews.length > 0) {
                        console.log("Este es el ID de la vista", this.actionViews[0].viewID)
                        
                        if (!this.actionViews[0].viewID)
                            
                            //if (this.actionViews[0].viewID == 2856) {
                            console.log("Entre a la vista para Reporte de pagos en gastos")
                        
                        
                            this.$buttons.find('.oe_action_button_to_call_wizard').click(this.proxy('action_def_reporte_gastos'));
                        
                        
                        //} 
                    }
                   }
            },
        
            action_def_reporte_gastos: function (e) {
                console.log("Hola")
                event.preventDefault();
                var self = this;
                self.do_action({
                    name: "Reporte de pagos",
                    type: 'ir.actions.act_window',
                    res_model: 'gasto.pago.reporte',
                    view_mode: 'form',
                    view_type: 'form',
                    view_id: 'view_gastos_pagos_reporte',
                    views: [[false, 'form']],
                    target: 'new',
                });
    
            },
        });
    
        $('#contadorBNActual').on('change', function(e) {
            console.log("Entro en el onchange")
            $('#textoInformativo').val('Hola mundo')
        });
    
    });