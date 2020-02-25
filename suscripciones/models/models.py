# -*- coding: utf-8 -*-

from odoo import models, fields, api

class saleSub(models.Model):
    _inherit = "sale.subscription"
    
    notasxD = fields.Text(string="Notas")
    
    """
    def _prepare_invoice_lines(self, fiscal_position):
        self.ensure_one()
        fiscal_position = self.env['account.fiscal.position'].browse(fiscal_position)
        mono=0
        color=0
        maximoMono=0
        maximoColor=0
        for ser in self.x_studio_nmeros_de_serie:
            mono=mono+ser.x_studio_impresiones
            colo=color+ser.x_studio_impresiones_color
        for line in self.recurring_invoice_line_ids:
            if('Renta base' in line.product_id.name):
                for line2 in self.recurring_invoice_line_ids:
                    if('Clic color' in line2.product_id.name):
                        maximoColor=line2.quantity
                    if('Clic mono' in line2.product_id.name):
                        maximoMono=line2.quantity
                for line3 in self.recurring_invoice_line_ids:
                    if(mono>maximoMono):
                        if('Clic excedente monocromático' in line3.product_id.name):
                            line3.quantity=mono-maximoMono
                    if(color>maximoColor):
                        if('Clic excedente color' in line3.product_id.name):
                            line3.quantity=color-maximoColor
            if('Renta global' == line.product_id.name):
                break
            if('Renta global + costo' in line.product_id.name):
                break
            copia=self.recurring_invoice_line_ids
            #for l in self.recurring_invoice_line_ids:
             #   if('Clic excedente monocromático' in l.product_id.name):
              #      l.quantity=0
               # if('Clic excedente color' in l.product_id.name):
                #    l.quantity=0   
        return [(0, 0, self._prepare_invoice_line(line, fiscal_position)) for line in copia]
    """
