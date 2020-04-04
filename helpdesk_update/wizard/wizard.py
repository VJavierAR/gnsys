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
    editarZona = fields.Boolean(string = 'Editar zona', store=True, default=False)
    zona = fields.Selection([('SUR','SUR'),('NORTE','NORTE'),('PONIENTE','PONIENTE'),('ORIENTE','ORIENTE'),('CENTRO','CENTRO'),('DISTRIBUIDOR','DISTRIBUIDOR'),('MONTERREY','MONTERREY'),('CUERNAVACA','CUERNAVACA'),('GUADALAJARA','GUADALAJARA'),('QUERETARO','QUERETARO'),('CANCUN','CANCUN'),('VERACRUZ','VERACRUZ'),('PUEBLA','PUEBLA'),('TOLUCA','TOLUCA'),('LEON','LEON'),('COMODIN','COMODIN'),('VILLAHERMOSA','VILLAHERMOSA'),('MERIDA','MERIDA'),('ALTAMIRA','ALTAMIRA'),('COMODIN','COMODIN'),('DF00','DF00'),('SAN LP','SAN LP'),('ESTADO DE MÉXICO','ESTADO DE MÉXICO'),('Foraneo Norte','Foraneo Norte'),('Foraneo Sur','Foraneo Sur')], string = 'Zona', store = True)

    def creaComentario(self):
        self.env['helpdesk.diagnostico'].create({'ticketRelacion': self.ticket_id.id
                                                ,'comentario': self.comentario
                                                ,'estadoTicket': self.ticket_id.stage_id.name
                                                ,'evidencia': [(6,0,self.evidencia.ids)]
                                                ,'mostrarComentario': self.check
                                                })
        if self.editarZona:
            self.ticket_id.write({'x_studio_zona': self.zona
                                , 'x_studio_field_6furK': self.zona
                                })
        if self.ticket_id.env.user.has_group('studio_customization.grupo_de_tecnicos_fi_6cce8af2-f2d0-4449-b629-906fb2c16636') and self.evidencia:
            self.ticket_id.write({'stage_id': 3})
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



class HelpDeskCerrarConComentario(TransientModel):
    _name = 'helpdesk.comentario.cerrar'
    _description = 'HelpDesk Cerrar Con Comentario'
    check = fields.Boolean(string = 'Mostrar en reporte', default = False,)
    ticket_id = fields.Many2one("helpdesk.ticket")
    diagnostico_id = fields.One2many('helpdesk.diagnostico', 'ticketRelacion', string = 'Diagnostico', compute = '_compute_diagnosticos')
    estado = fields.Char('Estado previo a cerrar el ticket', compute = "_compute_estadoTicket")
    comentario = fields.Text('Comentario')
    evidencia = fields.Many2many('ir.attachment', string = "Evidencias")

    def cerrarTicketConComentario(self):

      if self.ticket_id.stage_id.name == 'Resuelto' or self.ticket_id.stage_id.name == 'Abierto' or self.ticket_id.stage_id.name == 'Asignado' or self.ticket_id.stage_id.name == 'Atención' and self.ticket_id.estadoCerrado == False:
        self.env['helpdesk.diagnostico'].create({'ticketRelacion': self.ticket_id.id
                                                ,'comentario': self.comentario
                                                ,'estadoTicket': self.ticket_id.stage_id.name
                                                ,'evidencia': [(6,0,self.evidencia.ids)]
                                                ,'mostrarComentario': self.check
                                                })
        self.ticket_id.write({'stage_id': 18 
                            , 'estadoResueltoPorDocTecnico': True
                            , 'estadoAtencion': True
                            })
        mess = 'Ticket "' + str(self.ticket_id.id) + '" cerrado y último Diagnostico / Comentario añadido al ticket "' + str(self.ticket_id.id) + '" de forma exitosa. \n\nComentario agregado: ' + str(self.comentario) + '.'
        wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mess})
        view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
        return {
            'name': _('Ticket cerrado !!!'),
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




class HelpDeskDetalleSerie(TransientModel):
    _name = 'helpdesk.detalle.serie'
    _description = 'HelpDesk Detalle Serie'
    ticket_id = fields.Many2one("helpdesk.ticket")
    historicoTickets = fields.One2many('dcas.dcas', 'serie', string = 'Historico de tickets', compute='_compute_historico_tickets')
    lecturas = fields.One2many('dcas.dcas', 'serie', string = 'Lecturas', compute='_compute_lecturas')
    toner = fields.One2many('dcas.dcas', 'serie', string = 'Tóner', compute='_compute_toner')
    historicoDeComponentes = fields.One2many('x_studio_historico_de_componentes', 'x_studio_field_MH4DO', string = 'Historico de Componentes', compute='_compute_historico_de_componentes')
    movimientos = fields.One2many('stock.move.line', 'lot_id', string = 'Movimientos', compute='_compute_movimientos')
    serie = fields.Text(string = "Serie", compute = '_compute_serie_nombre')

    def _compute_serie_nombre(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.serie = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].name

    def _compute_historico_tickets(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.historicoTickets = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].x_studio_field_Yxv2m.ids

    def _compute_lecturas(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.lecturas = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].x_studio_field_PYss4.ids

    def _compute_toner(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.toner = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].x_studio_toner_1.ids

    def _compute_historico_de_componentes(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.historicoDeComponentes = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].x_studio_histrico_de_componentes.ids

    def _compute_movimientos(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.movimientos = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].x_studio_move_line.ids

class HelpDeskAlerta(TransientModel):
    _name = 'helpdesk.alerta'
    _description = 'HelpDesk Alerta'
    
    ticket_id = fields.Many2one("helpdesk.ticket")
    mensaje = fields.Text('Mensaje')
    

class HelpDeskAlertaNumeroDeSerie(TransientModel):
    _name = 'helpdesk.alerta.series'
    _description = 'HelpDesk Alerta para series existentes'
    
    ticket_id = fields.Many2one("helpdesk.ticket")
    ticket_id_existente = fields.Integer(string = 'Ticket existente', default = 0)
    mensaje = fields.Text('Mensaje')

    def abrirTicket(self):
        """
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
        """
        return {
                "type": "ir.actions.act_url",
                "url": "https://gnsys-corp.odoo.com/web#id= " + str(self.ticket_id_existente) + " &action=400&active_id=9&model=helpdesk.ticket&view_type=form&menu_id=406",
                "target": "new",
                }

    def abrirTicketCreado(self):
        return {
                "type": "ir.actions.act_url",
                "url": "https://gnsys-corp.odoo.com/web#id= " + str(self.ticket_id.id) + " &action=400&active_id=9&model=helpdesk.ticket&view_type=form&menu_id=406",
                "target": "new",
                }

    def action_refresh(self):
        # apply the logic here
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
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
                                        , default='contact', string = "Tipo de dirección", store=True)
    subtipo = fields.Selection([('Contacto comercial','Contacto comercial')
                                ,('Contacto sistemas','Contacto sistemas')
                                ,('Contacto para pagos','Contacto parra pagos')
                                ,('Contacto para compras','Contacto para compras')
                                ,('Representante legal','Representante legal')
                                ,('Contacto de localidad','Contacto de localidad')
                                ,('private','Dirección Privada')]
                                , string = "Subtipo", default = 'Contacto de localidad', store=True)
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
    contadorBNActual = fields.Integer(string='Contador B/N Actual', default = 0)
    contadorColorMesa = fields.Integer(string='Contador Color Mesa', compute = '_compute_actualizaContadorColorMesa')
    negroProcentaje = fields.Integer(string='% Negro')
    bnColor = fields.Text(string='Color o BN', compute = '_compute_actualizaColor')
    
    @api.depends('ticket_id')
    def _compute_contadorBNMesa(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            if self.contadorBNActual == 0:
                for serie in self.ticket_id.x_studio_equipo_por_nmero_de_serie:
                    self.contadorBNMesa = int(serie.x_studio_contador_bn_mesa)
                    self.contadorColorMesa = int(serie.x_studio_contador_color_mesa)
                    self.bnColor = serie.x_studio_color_bn
            else:
                self.contadorBNMesa = self.contadorBNActual

    def _compute_actualizaColor(self):
        for serie in self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.bnColor = str(serie.x_studio_color_bn)

    def _compute_actualizaContadorColorMesa(self):
        for serie in self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.contadorColorMesa = int(serie.x_studio_contador_color_mesa)
    
    def modificarContadores(self):          
        for c in self.ticket_id.x_studio_equipo_por_nmero_de_serie:                                       
            q = 'stock.production.lot'              
            if str(c.x_studio_color_bn) == 'B/N':
                if int(self.contadorBNActual) >= int(c.x_studio_contador_bn):
                    negrot = c.x_studio_contador_bn_mesa
                    colort = c.x_studio_contador_color_mesa
                    rr = self.env['dcas.dcas'].create({'serie' : c.id
                                                    , 'contadorMono' : self.contadorBNActual
                                                    #, 'x_studio_contador_color_anterior':colort
                                                    #, 'contadorColor' :self.contadorColorMesa
                                                    , 'x_studio_tickett':self.ticket_id.id
                                                    , 'x_studio_contador_mono_anterior_1':negrot  
                                                    , 'fuente':q
                                                  })                  
                    self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.ticket_id.x_studio_id_ticket, 'estadoTicket': 'captura ', 'write_uid':  self.env.user.name, 'comentario': 'bn '+str(c.x_studio_contador_bn_a_capturar)})

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



class helpdesk_crearconserie(TransientModel):
    _name = 'helpdesk.crearconserie'
    _description = 'HelpDesk crear ticket desde la serie'

    serie = fields.Many2many('stock.production.lot', string = 'Serie', store = True)
    clienteRelacion = fields.Many2one('res.partner', string = 'Cliente', default=False, store = True)
    localidadRelacion = fields.Many2one('res.partner', string = 'Localidad', store = True)

    cliente = fields.Text(string = 'Cliente', store = True)
    idCliente = fields.Text(string = 'idCliente', store=True, default=0)
    localidad = fields.Text(string = 'Localidad', store = True)
    zonaLocalidad = fields.Selection([('SUR','SUR'),('NORTE','NORTE'),('PONIENTE','PONIENTE'),('ORIENTE','ORIENTE'),('CENTRO','CENTRO'),('DISTRIBUIDOR','DISTRIBUIDOR'),('MONTERREY','MONTERREY'),('CUERNAVACA','CUERNAVACA'),('GUADALAJARA','GUADALAJARA'),('QUERETARO','QUERETARO'),('CANCUN','CANCUN'),('VERACRUZ','VERACRUZ'),('PUEBLA','PUEBLA'),('TOLUCA','TOLUCA'),('LEON','LEON'),('COMODIN','COMODIN'),('VILLAHERMOSA','VILLAHERMOSA'),('MERIDA','MERIDA'),('ALTAMIRA','ALTAMIRA'),('COMODIN','COMODIN'),('DF00','DF00'),('SAN LP','SAN LP'),('ESTADO DE MÉXICO','ESTADO DE MÉXICO'),('Foraneo Norte','Foraneo Norte'),('Foraneo Sur','Foraneo Sur')], string = 'Zona', store = True)
    idLocaliidad = fields.Text(string = 'idLocaliidad', store=True, default=0)
    nombreContactoLocalidad = fields.Text(string = 'Contacto de localidad', store = True)
    telefonoContactoLocalidad = fields.Text(string = 'Teléfono de contacto', store = True)
    movilContactoLocalidad = fields.Text(string = 'Movil de contacto', store = True)
    correoContactoLocalidad = fields.Text(string = 'Correo electronico de contacto', store = True)

    direccionCalleNombre = fields.Text(string = 'Calle', store = True)
    direccionNumeroExterior = fields.Text(string = 'Número exterior', store = True)
    direccionNumeroInterior = fields.Text(string = 'Número interior', store = True)
    direccionColonia = fields.Text(string = 'Colonia', store = True)
    direccionLocalidad = fields.Text(string = 'Localidad', store = True)
    direccionCiudad = fields.Text(string = 'Ciudad', store = True)
    direccionEstado = fields.Text(string = 'Estado', store = True)
    direccionCodigoPostal = fields.Text(string = 'Código postal', store = True)

    ticket_id_existente = fields.Integer(string = 'Ticket existente', default = 0, store = True)
    textoTicketExistente = fields.Text(string = ' ', store = True)

    def abrirTicket(self):
        return {
                "type": "ir.actions.act_url",
                "url": "https://gnsys-corp.odoo.com/web#id= " + str(self.ticket_id_existente) + " &action=400&active_id=9&model=helpdesk.ticket&view_type=form&menu_id=406",
                "target": "new",
                }


    @api.onchange('clienteRelacion', 'localidadRelacion')
    def actualiza_dominio_en_numeros_de_serie(self):
        #for record in self:
        if self.clienteRelacion.id or self.localidadRelacion.id:
            _logger.info("Entre porque existe: " + str(self.clienteRelacion) + ' loc: ' + str(self.localidadRelacion))
            zero = 0
            dominio = []
            dominioT = []
            
            #for record in self:
            id_cliente = self.clienteRelacion.id
            #id_cliente = record.x_studio_id_cliente
            id_localidad = self.localidadRelacion.id

            self.idCliente = id_cliente
            self.idLocaliidad = id_localidad

            if id_cliente != zero:
              #raise Warning('entro1')
              dominio = ['&', ('x_studio_categoria_de_producto_3.name','=','Equipo'), ('x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id', '=', id_cliente)]
              #dominioT = ['&', ('serie.x_studio_categoria_de_producto_3.name','=','Equipo'), ('serie.x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id', '=', id_cliente)]  
              
            else:
              #raise Warning('entro2')
              dominio = [('x_studio_categoria_de_producto_3.name','=','Equipo')]
              #dominioT = [('serie.x_studio_categoria_de_producto_3.name','=','Equipo')]
              
            if id_cliente != zero and id_localidad != zero:
              #raise Warning('entro3')
              dominio = ['&', '&', ('x_studio_categoria_de_producto_3.name','=','Equipo'), ('x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id', '=', id_cliente),('x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.id','=',id_localidad)]
              #dominioT = ['&', '&', ('serie.x_studio_categoria_de_producto_3.name','=','Equipo'), ('serie.x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id', '=', id_cliente),('serie.x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.id','=',id_localidad)]

            if id_localidad == zero and id_cliente != zero:
              #raise Warning('entro4')
              dominio = ['&', ('x_studio_categoria_de_producto_3.name','=','Equipo'), ('x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id', '=', id_cliente)]
              #dominioT = ['&', ('serie.x_studio_categoria_de_producto_3.name','=','Equipo'), ('serie.x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id', '=', id_cliente)]

            if id_cliente == zero and id_localidad == zero:
              #raise Warning('entro5')
              dominio = [('x_studio_categoria_de_producto_3.name', '=', 'Equipo')]
              #dominio = [('serie.x_studio_categoria_de_producto_3.name', '=', 'Equipo')]
              
            action = {'domain':{'serie': dominio}}
            
            return action
        else:
          _logger.info("Entre porque no existe: " + str(self.clienteRelacion) + ' loc: ' + str(self.localidadRelacion))
          dominio = [('x_studio_categoria_de_producto_3.name', '=', 'Equipo')]
          action = {'domain':{'serie': dominio}}
          return action

    

    
    @api.onchange('localidadRelacion')
    def cambia_localidad(self):
      if self.localidadRelacion:
        self.cliente = self.clienteRelacion.name
        self.localidad = self.localidadRelacion.name
        self.zonaLocalidad = self.localidadRelacion.x_studio_field_SqU5B

        loc = self.localidadRelacion.id
        idLoc = self.env['res.partner'].search([['parent_id', '=', loc],['x_studio_subtipo', '=', 'Contacto de localidad']], order='create_date desc', limit=1)
        if idLoc:
            self.nombreContactoLocalidad = idLoc[0].name
            self.telefonoContactoLocalidad = idLoc[0].phone
            self.movilContactoLocalidad = idLoc[0].mobile
            self.correoContactoLocalidad = idLoc[0].email

        else:
            self.nombreContactoLocalidad = ''
            self.telefonoContactoLocalidad = ''
            self.movilContactoLocalidad = ''
            self.correoContactoLocalidad = ''

        self.direccionCalleNombre = self.localidadRelacion.street_name
        self.direccionNumeroExterior = self.localidadRelacion.street_number
        self.direccionNumeroInterior = self.localidadRelacion.street_number2
        self.direccionColonia = self.localidadRelacion.l10n_mx_edi_colony
        self.direccionLocalidad = self.localidadRelacion.l10n_mx_edi_locality
        self.direccionCiudad = self.localidadRelacion.city
        self.direccionEstado = self.localidadRelacion.state_id.name
        self.direccionCodigoPostal = self.localidadRelacion.zip
      else:
        self.serie = ''

        self.cliente = ''
        self.localidad = ''
        self.zonaLocalidad = ''
        self.idLocaliidad = ''

        self.nombreContactoLocalidad = ''
        self.telefonoContactoLocalidad = ''
        self.movilContactoLocalidad = ''
        self.correoContactoLocalidad = ''

        self.direccionCalleNombre = ''
        self.direccionNumeroExterior = ''
        self.direccionNumeroInterior = ''
        self.direccionColonia = ''
        self.direccionLocalidad = ''
        self.direccionCiudad = ''
        self.direccionEstado = ''
        self.direccionCodigoPostal = ''

  

    
    @api.onchange('clienteRelacion')
    def cambia_cliente(self):
      if not self.clienteRelacion:
        self.localidadRelacion = ''
        self.serie = ''

        self.cliente = ''
        self.localidad = ''
        self.zonaLocalidad = ''
        self.idLocaliidad = ''

        self.nombreContactoLocalidad = ''
        self.telefonoContactoLocalidad = ''
        self.movilContactoLocalidad = ''
        self.correoContactoLocalidad = ''

        self.direccionCalleNombre = ''
        self.direccionNumeroExterior = ''
        self.direccionNumeroInterior = ''
        self.direccionColonia = ''
        self.direccionLocalidad = ''
        self.direccionCiudad = ''
        self.direccionEstado = ''
        self.direccionCodigoPostal = ''
    

    @api.onchange('serie')
    def cambia_serie(self):
        if self.serie:
            _my_object = self.env['helpdesk.crearconserie']
            if len(self.serie) > 1:
                mensajeTitulo = "Alerta!!!"
                mensajeCuerpo = "No puede capturar más de una serie."
                raise exceptions.Warning(mensajeCuerpo)
            else:
                query = "select h.id from helpdesk_ticket_stock_production_lot_rel s, helpdesk_ticket h where h.id=s.helpdesk_ticket_id and h.stage_id!=18 and h.team_id!=8 and  h.active='t' and stock_production_lot_id = " +  str(self.serie[0].id) + " limit 1;"
                #query = "select h.id from helpdesk_ticket_stock_production_lot_rel s, helpdesk_ticket h where h.id=s.helpdesk_ticket_id and h.id!=" + str(ticket.x_studio_id_ticket) + "  and h.stage_id!=18 and h.team_id!=8 and  h.active='t' and stock_production_lot_id = " +  str(self.serie[0].id) + " limit 1;"
                self.env.cr.execute(query)                        
                informacion = self.env.cr.fetchall()
                if len(informacion) > 0:
                  self.textoTicketExistente = "<br/><br/><h1>Esta serie ya tiene un ticket en proceso.</h1><br/><br/><h3>El ticket en proceso es:" + str(informacion[0][0]) + "</h3>"
                  self.ticket_id_existente = int(informacion[0][0])
                else:
                  self.ticket_id_existente = 0
                  self.textoTicketExistente = ''
                if self.serie[0].x_studio_move_line:
                    self.cliente = self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.name
                    self.idCliente = self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id
                    self.clienteRelacion = self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id
                    self.localidad = self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.name
                    self.zonaLocalidad = self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.x_studio_field_SqU5B
                    self.idLocaliidad = self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.id
                    self.localidadRelacion = self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.id

                    self.direccionCalleNombre = self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.street_name
                    self.direccionNumeroExterior = self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.street_number
                    self.direccionNumeroInterior = self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.street_number2
                    self.direccionColonia = self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.l10n_mx_edi_colony
                    self.direccionLocalidad = self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.l10n_mx_edi_locality
                    self.direccionCiudad = self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.city
                    self.direccionEstado = self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.state_id.name
                    self.direccionCodigoPostal = self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.zip
                    #self.direccion = self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.

                    _my_object.write({'idCliente' : self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id
                                    ,'idLocaliidad': self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.id
                                    })
                    loc = self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.id
                    
                    idLoc = self.env['res.partner'].search([['parent_id', '=', loc],['x_studio_subtipo', '=', 'Contacto de localidad']], order='create_date desc', limit=1)
                    
                    if idLoc:
                        self.nombreContactoLocalidad = idLoc[0].name
                        self.telefonoContactoLocalidad = idLoc[0].phone
                        self.movilContactoLocalidad = idLoc[0].mobile
                        self.correoContactoLocalidad = idLoc[0].email

                    else:
                        self.nombreContactoLocalidad = ''
                        self.telefonoContactoLocalidad = ''
                        self.movilContactoLocalidad = ''
                        self.correoContactoLocalidad = ''
                    

                    
                else:
                    mensajeTitulo = "Alerta!!!"
                    mensajeCuerpo = "No existe una locación del equipo."
                    warning = {'title': _(mensajeTitulo)
                            , 'message': _(mensajeCuerpo),
                    }
                    return {'warning': warning}
        else:

            self.ticket_id_existente = 0
            self.textoTicketExistente = ''
            
            self.cliente = ''
            self.localidad = ''
            self.zonaLocalidad = ''
            self.idLocaliidad = ''

            self.clienteRelacion = ''
            self.localidadRelacion = ''

            self.nombreContactoLocalidad = ''
            self.telefonoContactoLocalidad = ''
            self.movilContactoLocalidad = ''
            self.correoContactoLocalidad = ''

            self.direccionCalleNombre = ''
            self.direccionNumeroExterior = ''
            self.direccionNumeroInterior = ''
            self.direccionColonia = ''
            self.direccionLocalidad = ''
            self.direccionCiudad = ''
            self.direccionEstado = ''
            self.direccionCodigoPostal = ''

    def crearTicket(self):
        if self.serie:
            messageTemp = ''
            ticket = self.env['helpdesk.ticket'].create({'stage_id': 89 
                                                ,'x_studio_equipo_por_nmero_de_serie': [(6,0,self.serie.ids)]
                                                ,'partner_id': int(self.idCliente)
                                                ,'x_studio_empresas_relacionadas': int(self.idLocaliidad)
                                                ,'team_id': 9
                                                ,'x_studio_field_6furK': self.zonaLocalidad
                                                })
            ticket.write({'partner_id': int(self.idCliente)
                        ,'x_studio_empresas_relacionadas': int(self.idLocaliidad)
                        ,'team_id': 9
                        ,'x_studio_field_6furK': self.zonaLocalidad
                        })
            query = "update helpdesk_ticket set \"partner_id\" = " + str(self.idCliente) + ", \"x_studio_empresas_relacionadas\" =" + str(self.idLocaliidad) + " where id = " + str(ticket.id) + ";"
            self.env.cr.execute(query)
            self.env.cr.commit()
            ticket._compute_datosCliente()
            query = "select h.id from helpdesk_ticket_stock_production_lot_rel s, helpdesk_ticket h where h.id=s.helpdesk_ticket_id and h.id!=" + str(ticket.x_studio_id_ticket) + "  and h.stage_id!=18 and h.team_id!=8 and  h.active='t' and stock_production_lot_id = " +  str(ticket.x_studio_equipo_por_nmero_de_serie[0].id) + " limit 1;"
            self.env.cr.execute(query)                        
            informacion = self.env.cr.fetchall()
            wiz = ''
            mensajeTitulo = "Ticket generado!!!"
            if len(informacion) > 0:
                mensajeCuerpo = ('Se creo un ticket que esta en proceso con la serie "' + self.serie.name + '" seleccionada. \n Ticket existente: ' + str(informacion[0][0]) + '\n ')
                wiz = self.env['helpdesk.alerta.series'].create({'ticket_id': ticket.id, 'ticket_id_existente': informacion[0][0], 'mensaje': mensajeCuerpo})
            else:
                mensajeCuerpo = "Se creo el ticket '" + str(ticket.id) + "' con el número de serie " + self.serie.name + "\n\n"
                wiz = self.env['helpdesk.alerta.series'].create({'ticket_id': ticket.id, 'mensaje': mensajeCuerpo})
            
            #wiz = self.env['helpdesk.alerta.series'].create({'ticket_id': ticket.id, 'mensaje': mensajeCuerpo})
            view = self.env.ref('helpdesk_update.view_helpdesk_alerta_series')
            return {
                    'name': _(mensajeTitulo),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'helpdesk.alerta.series',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': self.env.context,
                    }
        elif self.clienteRelacion.id and self.localidadRelacion.id:
          messageTemp = ''
          ticket = self.env['helpdesk.ticket'].create({'stage_id': 89 
                                              #,'x_studio_equipo_por_nmero_de_serie': [(6,0,self.serie.ids)]
                                              ,'partner_id': int(self.idCliente)
                                              ,'x_studio_empresas_relacionadas': int(self.idLocaliidad)
                                              ,'team_id': 9
                                              ,'x_studio_field_6furK': self.zonaLocalidad
                                              })
          ticket.write({'partner_id': int(self.idCliente)
                      ,'x_studio_empresas_relacionadas': int(self.idLocaliidad)
                      ,'team_id': 9
                      ,'x_studio_field_6furK': self.zonaLocalidad
                      })
          #query = "update helpdesk_ticket set \"partner_id\" = " + str(self.idCliente) + ", \"x_studio_empresas_relacionadas\" =" + str(self.idLocaliidad) + " where id = " + str(ticket.id) + ";"
          #self.env.cr.execute(query)
          #self.env.cr.commit()
          ticket._compute_datosCliente()
          #query = "select h.id from helpdesk_ticket_stock_production_lot_rel s, helpdesk_ticket h where h.id=s.helpdesk_ticket_id and h.id!=" + str(ticket.x_studio_id_ticket) + "  and h.stage_id!=18 and h.team_id!=8 and  h.active='t' and stock_production_lot_id = " +  str(ticket.x_studio_equipo_por_nmero_de_serie[0].id) + " limit 1;"            
          #self.env.cr.execute(query)                        
          #informacion = self.env.cr.fetchall()
          wiz = ''
          mensajeTitulo = "Ticket generado!!!"
          #mensajeCuerpo = "Se creo el ticket '" + str(ticket.id) + "' sin número de serie para cliente " + self.cliente + " con localidad " + self.localidad + "\n\n"
          mensajeCuerpo = "Se creo el ticket '" + str(ticket.id) + "' sin número de serie. \n\n"
          wiz = self.env['helpdesk.alerta.series'].create({'ticket_id': ticket.id, 'mensaje': mensajeCuerpo})
          view = self.env.ref('helpdesk_update.view_helpdesk_alerta_series')
          return {
                  'name': _(mensajeTitulo),
                  'type': 'ir.actions.act_window',
                  'view_type': 'form',
                  'view_mode': 'form',
                  'res_model': 'helpdesk.alerta.series',
                  'views': [(view.id, 'form')],
                  'view_id': view.id,
                  'target': 'new',
                  'res_id': wiz.id,
                  'context': self.env.context,
                  }
