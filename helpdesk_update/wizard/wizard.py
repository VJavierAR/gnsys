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
    contadorBN = fields.Integer(string='Contador B/N')
    contadorBNMesa = fields.Integer(string='Contador B/N Mesa')
    contadorBNActual = fields.Integer(string='Contador B/N Actual')
    contadorColorMesa = fields.Integer(string='Contador Color Mesa')
    negroProcentaje = fields.Integer(string='% Negro')
    #CREAR COMENTARIO
    
    def modificarContadores(self):
        self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.ticket_id.id
                                                ,'comentario':self.comentario
                                                ,'estadoTicket':self.estado,'evidencia':[(6,0,self.evidencia.ids)]
                                                ,'mostrarComentario':self.check
                                                })

