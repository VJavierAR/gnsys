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
            for serie in self.ticket_id.x_studio_equipo_por_nmero_de_serie:
                self.contadorBNMesa = int(serie.x_studio_contador_bn_mesa)
                self.contadorColorMesa = int(serie.x_studio_contador_color_mesa)
    
    def modificarContadores(self):
        for record in self:  
            for c in record.x_studio_equipo_por_nmero_de_serie:
              if self.team_id.id==8:
                q='helpdesk.ticket'
              else:
                q='stock.production.lot'
              #if str(c.x_studio_field_A6PR9) =='Negro':
              if str(c.x_studio_color_bn) == 'B/N':
                  if int(c.x_studio_contador_bn_a_capturar) >= int(c.x_studio_contador_bn):
                      if self.team_id.id==8:
                         negrot = c.x_studio_contador_bn
                         colort = c.x_studio_contador_color
                      else:
                         negrot = c.x_studio_contador_bn_mesa
                         colort = c.x_studio_contador_color_mesa                        
                      rr=self.env['dcas.dcas'].create({'serie' : c.id
                                                    , 'contadorMono' : c.x_studio_contador_bn_a_capturar
                                                    ,'x_studio_contador_color_anterior':colort
                                                    , 'contadorColor' :c.x_studio_contador_color_a_capturar
                                                    ,'x_studio_contador_mono_anterior_1':negrot
                                                    ,'porcentajeNegro':c.x_studio__negro
                                                    ,'porcentajeCian':c.x_studio__cian      
                                                    ,'porcentajeAmarillo':c.x_studio__amarrillo      
                                                    ,'porcentajeMagenta':c.x_studio__magenta
                                                    ,'x_studio_descripcion':self.name
                                                    ,'x_studio_tickett':self.x_studio_id_ticket
                                                    ,'x_studio_hoja_de_estado':c.x_studio_evidencias
                                                    ,'x_studio_usuariocaptura':self.env.user.name
                                                    ,'fuente':q
                                                    ,'x_studio_rendimiento':int(c.x_studio_rendimiento)/abs(int(c.x_studio_contador_bn_a_capturar)-int(negrot))
                                                  })                  
                      self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.x_studio_id_ticket, 'estadoTicket': 'captura ', 'write_uid':  self.env.user.name, 'comentario':'capturas :' + str('Mono'+str(c.x_studio_contador_bn_a_capturar)+', Color '+str(c.x_studio_contador_color_a_capturar)+', Amarillo '+str(c.x_studio__amarrillo)+', Cian '+str(c.x_studio__cian)+', Negro '+str(c.x_studio__negro)+', Magenta '+str(c.x_studio__magenta)+', % de rendimiento '+str(rr.x_studio_rendimiento))})
                  else :
                    raise exceptions.ValidationError("Contador Monocromatico Menor")                     
              #if str(c.x_studio_field_A6PR9) != 'Negro':       
              if str(c.x_studio_color_bn) != 'B/N':
                  if int(c.x_studio_contador_color_a_capturar) >= int(c.x_studio_contador_color) and int(c.x_studio_contador_bn_a_capturar) >= int(c.x_studio_contador_bn):                      
                      if self.team_id.id==8:
                         negrot = c.x_studio_contador_bn
                         colort = c.x_studio_contador_color
                      else:
                         negrot = c.x_studio_contador_bn_mesa
                         colort = c.x_studio_contador_color_mesa
                      rr=self.env['dcas.dcas'].create({'serie' : c.id
                                                    , 'contadorMono' : c.x_studio_contador_bn_a_capturar
                                                    ,'x_studio_contador_color_anterior':colort
                                                    , 'contadorColor' :c.x_studio_contador_color_a_capturar
                                                    ,'x_studio_contador_mono_anterior_1':negrot
                                                    ,'porcentajeNegro':c.x_studio__negro
                                                    ,'porcentajeCian':c.x_studio__cian      
                                                    ,'porcentajeAmarillo':c.x_studio__amarrillo      
                                                    ,'porcentajeMagenta':c.x_studio__magenta
                                                    ,'x_studio_descripcion':self.name
                                                    ,'x_studio_tickett':self.x_studio_id_ticket
                                                    ,'x_studio_hoja_de_estado':c.x_studio_evidencias
                                                    ,'x_studio_usuariocaptura':self.env.user.name
                                                    ,'fuente':q
                                                    ,'x_studio_rendimiento':int(c.x_studio_rendimiento)/abs(int(c.x_studio_contador_bn_a_capturar)-int(negrot))
                                                  })                  
                      self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.x_studio_id_ticket, 'estadoTicket': 'captura ', 'write_uid':  self.env.user.name, 'comentario':'capturas :' + str('Mono'+str(c.x_studio_contador_bn_a_capturar)+', Color '+str(c.x_studio_contador_color_a_capturar)+', Amarillo '+str(c.x_studio__amarrillo)+', Cian '+str(c.x_studio__cian)+', Negro '+str(c.x_studio__negro)+', Magenta '+str(c.x_studio__magenta)+', % de rendimiento '+str(rr.x_studio_rendimiento))})
                  else :
                    raise exceptions.ValidationError("Error al capturar debe ser mayor")

