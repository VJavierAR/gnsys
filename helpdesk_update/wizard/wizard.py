from odoo import fields, api
from odoo.models import TransientModel
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from odoo import exceptions, _

class HelpDeskComentario(TransientModel):
    _name = 'helpdesk.comentario'
    _description = 'HelpDesk Comentario'
    check = fields.Boolean(string='Mostrar en reporte',default=False,)
    ticket_id = fields.Many2one("helpdesk.ticket")
    diagnostico_id = fields.One2many('helpdesk.diagnostico', 'ticketRelacion', string = 'Diagnostico', compute='_compute_diagnosticos')
    estado = fields.Char('Estado', compute = "_compute_estadoTicket")
    comentario = fields.Text('Comentario')
    evidencia = fields.Many2many('ir.attachment', string="Evidencias")
    
    
    def creaComentario(self):
        self.env['helpdesk.diagnostico'].create({'ticketRelacion': self.ticket_id.id
                                                ,'comentario': self.comentario
                                                ,'estadoTicket': self.ticket_id.stage_id.name
                                                ,'evidencia': [(6,0,self.evidencia.ids)]
                                                ,'mostrarComentario': self.check
                                                })
        
        mess = 'Diagnostico / Comentario añadido al ticket "' + str(self.ticket_id.id) + '" de forma exitosa. \n\nComentario agregado: ' + str(self.comentario) + '. \n\nGenerado en el estado: ' + self.ticket_id.stage_id.name
        wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mess})
        view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
        return {
            'name': _('Diagnostico / Comentario exitoso !!!'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.alerta',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }



    def _compute_estadoTicket(self):
        self.estado = self.ticket_id.stage_id.name

    def _compute_diagnosticos(self):
        self.diagnostico_id = self.ticket_id.diagnosticos.ids


class HelpDeskAlerta(TransientModel):
    _name = 'helpdesk.alerta'
    _description = 'HelpDesk Alerta'
    
    ticket_id = fields.Many2one("helpdesk.ticket")
    mensaje = fields.Text('Mensaje')
    

class HelpDeskAlertaNumeroDeSerie(TransientModel):
    _name = 'helpdesk.alerta.series'
    _description = 'HelpDesk Alerta para series existentes'
    
    ticket_id = fields.Many2one("helpdesk.ticket")
    #ticket_id_existente = fields.Integer(string = 'Ticket existente')
    mensaje = fields.Text('Mensaje')


    def abrirTicket(self):
        name = 'Ticket'
        res_model = 'helpdesk.ticket' 
        view_name = 'helpdesk.helpdesk_ticket_view_form'
        view = self.env.ref(view_name)
        return {
                'name': _('Ticket'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'helpdesk.ticket',
                #'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'current',
                'res_id': self.ticket_id.id,
                'nodestroy': True
                }


class HelpDeskContacto(TransientModel):
    _name = 'helpdesk.contacto'
    _description = 'HelpDesk Contacto'
    ticket_id = fields.Many2one("helpdesk.ticket")
    
    tipoDeDireccion = fields.Selection([('contact','Contacto')
                                        ,('invoice','Dirección de facturación')
                                        ,('delivery','Dirección de envío')
                                        ,('other','Otra dirección')
                                        ,('private','Dirección Privada')]
                                        , default='contact', string="Tipo de dirección")
    subtipo = fields.Selection([('Contacto comercial','Contacto comercial')
                                ,('Contacto sistemas','Contacto sistemas')
                                ,('Contacto para pagos','Contacto parra pagos')
                                ,('Contacto para compras','Contacto para compras')
                                ,('private','Dirección Privada')]
                                , string = "Subtipo")
    nombreDelContacto = fields.Char(string='Nombre de contacto')
    titulo = fields.Many2one('res.partner.title', store=True, string='Titulo')
    puestoDeTrabajo = fields.Char(string='Puesto de trabajo')
    correoElectronico = fields.Char(string='Correo electrónico')
    telefono = fields.Char(string='Teléfono')
    movil = fields.Char(string='Móvil')
    notas = fields.Text(string="Notas")

    direccionNombreCalle = fields.Char(string='Nombre de la calle')
    direccionNumeroExterior = fields.Char(string='Número exterior')
    direccionNumeroInterior = fields.Char(string='Número interior')
    direccionColonia = fields.Char(string='Colonia')
    direccionLocalidad = fields.Char(string='Localidad')
    direccionCiudad = fields.Char(string='Ciudad', default='Ciudad de México')
    direccionCodigoPostal = fields.Char(string='Código postal')
    direccionPais = fields.Many2one('res.country', store=True, string='País', default='156')
    direccionEstado = fields.Many2one('res.country.state', store=True, string='Estado', domain="[('country_id', '=?', direccionPais)]")
    
    direccionZona = fields.Selection([('SUR','SUR')
                                      ,('NORTE','NORTE')
                                      ,('PONIENTE','PONIENTE')
                                      ,('ORIENTE','ORIENTE')
                                      ,('CENTRO','CENTRO')
                                      ,('DISTRIBUIDOR','DISTRIBUIDOR')
                                      ,('MONTERREY','MONTERREY')
                                      ,('CUERNAVACA','CUERNAVACA')
                                      ,('GUADALAJARA','GUADALAJARA')
                                      ,('QUERETARO','QUERETARO')
                                      ,('CANCUN','CANCUN')
                                      ,('VERACRUZ','VERACRUZ')
                                      ,('PUEBLA','PUEBLA')
                                      ,('TOLUCA','TOLUCA')
                                      ,('LEON','LEON')
                                      ,('COMODIN','COMODIN')
                                      ,('VILLAHERMOSA','VILLAHERMOSA')
                                      ,('MERIDA','MERIDA')
                                      ,('ALTAMIRA','ALTAMIRA')]
                                      , string = 'Zona')

    
    def agregarContactoALocalidad(self):
        mensajeTitulo = ''
        mensajeCuerpo = ''
        if self.ticket_id.x_studio_empresas_relacionadas.id != 0:
            contactoId = 0
            titulo = ''
            if len(self.titulo) == 0:
                titulo = ''
            else:
                titulo = self.titulo.id
            if self.tipoDeDireccion == "contact" and self.nombreDelContacto != False:
                contacto = self.sudo().env['res.partner'].create({'parent_id' : self.ticket_id.x_studio_empresas_relacionadas.id
                                                                 , 'type' : self.tipoDeDireccion
                                                                 , 'x_studio_subtipo' : self.subtipo
                                                                 , 'name' : self.nombreDelContacto
                                                                 , 'title' : titulo
                                                                 , 'function' : self.puestoDeTrabajo
                                                                 , 'email' : self.correoElectronico
                                                                 , 'phone' : self.telefono
                                                                 , 'mobile' : self.movil
                                                                 , 'comment' : self.notas
                                                                 , 'team_id': 1
                                                                })
                contactoId = contacto.id
            elif self.tipoDeDireccion == "delivery" and self.nombreDelContacto != False:
                contacto = self.sudo().env['res.partner'].create({'parent_id' : self.ticket_id.x_studio_empresas_relacionadas.id
                                                                 , 'type' : self.tipoDeDireccion
                                                                 , 'x_studio_subtipo' : self.subtipo
                                                                 , 'name' : self.nombreDelContacto
                                                                 , 'title' : titulo
                                                                 , 'function' : self.puestoDeTrabajo
                                                                 , 'email' : self.correoElectronico
                                                                 , 'phone' : self.telefono
                                                                 , 'mobile' : self.movil
                                                                 , 'comment' : self.notas
                                                                 , 'team_id': 1
                                                                  
                                                                 , 'street_name' : self.direccionNombreCalle
                                                                 , 'street_number' : self.direccionNumeroExterior
                                                                 , 'street_number2' : self.direccionNumeroInterior
                                                                 , 'l10n_mx_edi_colony' : self.direccionColonia
                                                                 , 'l10n_mx_edi_locality' : self.direccionLocalidad
                                                                 , 'city' : self.direccionCiudad
                                                                 , 'state_id' : self.direccionEstado.id
                                                                 , 'zip' : self.direccionCodigoPostal
                                                                 , 'country_id' : self.direccionPais.id
                                                                  
                                                                 , 'x_studio_field_SqU5B' : self.direccionZona
                                                                })
                contactoId = contacto.id
            #elif self.tipoDeDireccion != "delivery" or self.tipoDeDireccion != "contact":
            elif self.nombreDelContacto != False:
                contacto = self.sudo().env['res.partner'].create({'parent_id' : self.ticket_id.x_studio_empresas_relacionadas.id
                                                                 , 'type' : self.tipoDeDireccion
                                                                 , 'x_studio_subtipo' : self.subtipo
                                                                 , 'name' : self.nombreDelContacto
                                                                 , 'title' : titulo
                                                                 , 'function' : self.puestoDeTrabajo
                                                                 , 'email' : self.correoElectronico
                                                                 , 'phone' : self.telefono
                                                                 , 'mobile' : self.movil
                                                                 , 'comment' : self.notas
                                                                 , 'team_id': 1
                                                                  
                                                                 , 'street_name' : self.direccionNombreCalle
                                                                 , 'street_number' : self.direccionNumeroExterior
                                                                 , 'street_number2' : self.direccionNumeroInterior
                                                                 , 'l10n_mx_edi_colony' : self.direccionColonia
                                                                 , 'l10n_mx_edi_locality' : self.direccionLocalidad
                                                                 , 'city' : self.direccionCiudad
                                                                 , 'state_id' : self.direccionEstado.id
                                                                 , 'zip' : self.direccionCodigoPostal
                                                                 , 'country_id' : self.direccionPais.id
                                                                })
                contactoId = contacto.id
            else:
                mensajeTitulo = "Contacto sin nombre"
                mensajeCuerpo = "No es posible añadir un contacto sin nombre. Favor de indicar el nombre primero."
                #raise exceptions.except_orm(_(errorContactoSinNombre), _(mensajeContactoSinNombre))
            #self.env.cr.commit()
            if contactoId > 0:
                mensajeTitulo = "Contacto agregado." 
                mensajeCuerpo = "Contacto " + str(self.nombreDelContacto) + " agregado a la localidad " + str(self.ticket_id.x_studio_empresas_relacionadas.name)
                self.ticket_id.localidadContacto=contactoId
                #raise exceptions.except_orm(_(errorContactoGenerado), _(mensajeContactoGenerado))
            else:
                mensajeTitulo = "Contacto no agregado"
                mensajeCuerpo = "Contacto no agregado. Favor de verificar la información ingresada."
                #raise exceptions.except_orm(_(errorContactoNoGenerado), _(mensajeContactoNoGenerado))
        else:
            mensajeTitulo = "Contacto sin localidad"
            mensajeCuerpo = "No es posible añadir un contacto sin primero indicar la localidad. Favor de indicar la localidad primero."
            #raise exceptions.except_orm(_(errorContactoSinLocalidad), _(mensajeContactoSinLocalidad))
        
        wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
        view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
        return {
                'name': _(mensajeTitulo),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'helpdesk.alerta',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
                }



class helpdesk_contadores(TransientModel):
    _name = 'helpdesk.contadores'
    _description = 'HelpDesk Contadores'
    check = fields.Boolean(string='Solicitar tóner B/N', default=False,)
    ticket_id = fields.Many2one("helpdesk.ticket")
    
    contadorBNMesa = fields.Integer(string='Contador B/N Mesa', compute="_compute_contadorBNMesa")
    contadorBNActual = fields.Integer(string='Contador B/N Actual')
    contadorColorMesa = fields.Integer(string='Contador Color Mesa')
    negroProcentaje = fields.Integer(string='% Negro')
    bnColor = fields.Char(string='Color o BN')
    

    
    @api.depends('ticket_id')
    def _compute_contadorBNMesa(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            for serie in self.ticket_id.x_studio_equipo_por_nmero_de_serie:
                self.contadorBNMesa = int(serie.x_studio_contador_bn_mesa)
                self.contadorColorMesa = int(serie.x_studio_contador_color_mesa)
                self.bnColor= str(serie.x_studio_color_bn)

    
    def modificarContadores(self):          
        for c in self.ticket_id.x_studio_equipo_por_nmero_de_serie:                                       
            q='stock.production.lot'              
            if str(c.x_studio_color_bn) == 'B/N':
                if int(self.contadorBNActual) >= int(c.x_studio_contador_bn):
                    negrot = c.x_studio_contador_bn_mesa
                    colort = c.x_studio_contador_color_mesa                        
                    rr=self.env['dcas.dcas'].create({'serie' : c.id
                                                    , 'contadorMono' : self.contadorBNActual
                                                    ,'x_studio_contador_color_anterior':colort
                                                    , 'contadorColor' :self.contadorColorMesa
                                                    ,'x_studio_tickett':self.ticket_id.id
                                                    ,'x_studio_contador_mono_anterior_1':negrot  
                                                    ,'fuente':q
                                                  })                  
                    self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.ticket_id.x_studio_id_ticket, 'estadoTicket': 'captura ', 'write_uid':  self.env.user.name, 'comentario': 'bn '+str(c.x_studio_contador_bn_a_capturar)+' color '+str(c.x_studio_contador_color_a_capturar)})

                    mensajeTitulo = "Contador capturado!!!"
                    mensajeCuerpo = "Se capturo el contador."
                    wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
                    view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
                    return {
                            'name': _(mensajeTitulo),
                            'type': 'ir.actions.act_window',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_model': 'helpdesk.alerta',
                            'views': [(view.id, 'form')],
                            'view_id': view.id,
                            'target': 'new',
                            'res_id': wiz.id,
                            'context': self.env.context,
                            }
                else:
                    raise exceptions.ValidationError("Contador Monocromatico Menor")                                   
            if str(c.x_studio_color_bn) != 'B/N':
                if int(self.contadorColorMesa) >= int(c.x_studio_contador_color) and int(self.contadorBNActual) >= int(c.x_studio_contador_bn):                      
                    if self.team_id.id==8:
                        negrot = c.x_studio_contador_bn
                        colort = c.x_studio_contador_color
                    else:
                        negrot = c.x_studio_contador_bn_mesa
                        colort = c.x_studio_contador_color_mesa
                    rr=self.env['dcas.dcas'].create({'serie' : c.id
                                                    , 'contadorMono' : self.contadorBNActual
                                                    ,'x_studio_contador_color_anterior':colort
                                                    , 'contadorColor' :self.contadorColorMesa
                                                    ,'x_studio_tickett':self.ticket_id.id
                                                    ,'x_studio_contador_mono_anterior_1':negrot
                                                    ,'fuente':q
                                                  })   
                    self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.ticket_id.x_studio_id_ticket, 'estadoTicket': 'captura ', 'write_uid':  self.env.user.name, 'comentario': 'bn '+str(c.x_studio_contador_bn_a_capturar)+' color '+str(c.x_studio_contador_color_a_capturar)})
                    mensajeTitulo = "Contador capturado!!!"
                    mensajeCuerpo = "Se capturo el contador."
                    wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
                    view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
                    return {
                            'name': _(mensajeTitulo),
                            'type': 'ir.actions.act_window',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_model': 'helpdesk.alerta',
                            'views': [(view.id, 'form')],
                            'view_id': view.id,
                            'target': 'new',
                            'res_id': wiz.id,
                            'context': self.env.context,
                            }
                else:
                    raise exceptions.ValidationError("Error al capturar debe ser mayor")

