from odoo import fields, api
from odoo.models import TransientModel
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)

class HelpDeskComentario(TransientModel):
    _name = 'helpdesk.comentario'
    _description = 'HelpDesk Comentario'
    check = fields.Boolean(string='Mostrar en reporte',default=False,)
    ticket_id = fields.Many2one("helpdesk.ticket")
    estado=fields.Char('Estado')
    comentario=fields.Char('Comentario')
    evidencia = fields.Many2many('ir.attachment', string="Evidencias")
    #CREAR COMENTARIO
    
    def creaComentario(self):
        self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.ticket_id.id,'comentario':self.comentario,'estadoTicket':self.estado,'evidencia':[(6,0,self.evidencia.ids)],'mostrarComentario':self.check})


class helpdesk_contadores(TransientModel):
    _name = 'helpdesk.contadores'
    _description = 'HelpDesk Contadores'
    check = fields.Boolean(string='Solicitar tóner B/N', default=False,)
    ticket_id = fields.Many2one("helpdesk.ticket")
    
    contadorBNMesa = fields.Integer(string='Contador B/N Mesa', compute="_compute_contadorBNMesa")
    contadorBNActual = fields.Integer(string='Contador B/N Actual')
    contadorColorMesa = fields.Integer(string='Contador Color Mesa')
    negroProcentaje = fields.Integer(string='% Negro')
    

    
    @api.depends('ticket_id')
    def _compute_contadorBNMesa(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            _logger.info("ticket: " + str(self.ticket_id) + 'series' + str(self.ticket_id.x_studio_equipo_por_nmero_de_serie) )
            for serie in self.ticket_id.x_studio_equipo_por_nmero_de_serie:
                contadorBNMesa = int(serie.x_studio_contador_bn_mesa)
    
    def modificarContadores(self):
        self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.ticket_id.id
                                                ,'comentario':self.comentario
                                                ,'estadoTicket':self.estado,'evidencia':[(6,0,self.evidencia.ids)]
                                                ,'mostrarComentario':self.check
                                                })

