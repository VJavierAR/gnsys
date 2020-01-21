# -*- coding: utf-8 -*-

from odoo import _, models, fields, api, tools
from email.utils import formataddr
from odoo.exceptions import UserError
from odoo import exceptions, _
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)

class helpdesk_update(models.Model):
    #_inherit = ['mail.thread', 'helpdesk.ticket']
    _inherit = 'helpdesk.ticket'
    #priority = fields.Selection([('all','Todas'),('baja','Baja'),('media','Media'),('alta','Alta'),('critica','Critica')])
    zona_estados = fields.Selection([('Estado de México','Estado de México'), ('Campeche','Campeche'), ('Ciudad de México','Ciudad de México'), ('Yucatán','Yucatán'), ('Guanajuato','Guanajuato'), ('Puebla','Puebla'), ('Coahuila','Coahuila'), ('Sonora','Sonora'), ('Tamaulipas','Tamaulipas'), ('Oaxaca','Oaxaca'), ('Tlaxcala','Tlaxcala'), ('Morelos','Morelos'), ('Jalisco','Jalisco'), ('Sinaloa','Sinaloa'), ('Nuevo León','Nuevo León'), ('Baja California','Baja California'), ('Nayarit','Nayarit'), ('Querétaro','Querétaro'), ('Tabasco','Tabasco'), ('Hidalgo','Hidalgo'), ('Chihuahua','Chihuahua'), ('Quintana Roo','Quintana Roo'), ('Chiapas','Chiapas'), ('Veracruz','Veracruz'), ('Michoacán','Michoacán'), ('Aguascalientes','Aguascalientes'), ('Guerrero','Guerrero'), ('San Luis Potosí', 'San Luis Potosí'), ('Colima','Colima'), ('Durango','Durango'), ('Baja California Sur','Baja California Sur'), ('Zacatecas','Zacatecas')], track_visibility='onchange', store=True)
    estatus_techra = fields.Selection([('Cerrado','Cerrado'), ('Cancelado','Cancelado'), ('Cotización','Cotización'), ('Tiempo de espera','Tiempo de espera'), ('COTIZACION POR AUTORIZAR POR CLIENTE','COTIZACION POR AUTORIZAR POR CLIENTE'), ('Facturar','Facturar'), ('Refacción validada','Refacción validada'), ('Instalación','Instalación'), ('Taller','Taller'), ('En proceso de atención','En proceso de atención'), ('En Pedido','En Pedido'), ('Mensaje','Mensaje'), ('Resuelto','Resuelto'), ('Reasignación de área','Reasignación de área'), ('Diagnóstico de Técnico','Diagnóstico de Técnico'), ('Entregado','Entregado'), ('En Ruta','En Ruta'), ('Listo para entregar','Listo para entregar'), ('Espera de Resultados','Espera de Resultados'), ('Solicitud de refacción','Solicitud de refacción'), ('Abierto TFS','Abierto TFS'), ('Reparación en taller','Reparación en taller'), ('Abierto Mesa de Ayuda','Abierto Mesa de Ayuda'), ('Reabierto','Reabierto')], track_visibility='onchange', store=True)
    priority = fields.Selection([('0','Todas'),('1','Baja'),('2','Media'),('3','Alta'),('4','Critica')], track_visibility='onchange')
    x_studio_equipo_por_nmero_de_serie = fields.Many2many('stock.production.lot', store=True)
    #x_studio_equipo_por_nmero_de_serieRel = fields.Many2one('stock.production.lot', store=True)
    x_studio_empresas_relacionadas = fields.Many2one('res.partner', store=True, track_visibility='onchange', string='Localidad')
    historialCuatro = fields.One2many('x_historial_helpdesk','x_id_ticket',string='historial de ticket estados',store=True,track_visibility='onchange')
    documentosTecnico = fields.Many2many('ir.attachment', string="Evidencias Técnico")
    stage_id = fields.Many2one('helpdesk.stage', string='Stage', ondelete='restrict', track_visibility='onchange',group_expand='_read_group_stage_ids',readonly=True,copy=False,index=True, domain="[('team_ids', '=', team_id)]")
    productos = fields.One2many('product.product','id',string='Solicitudes',store=True)
    
    days_difference = fields.Integer(compute='_compute_difference',string='días de atraso')
    
    localidadContacto = fields.Many2one('res.partner', store=True, track_visibility='onchange', string='Localidad contacto', domain="['&',('parent_id.id','=',idLocalidadAyuda),('type','=','contact')]")
    
    tipoDeDireccion = fields.Selection([('contact','Contacto'),('invoice','Dirección de facturación'),('delivery','Dirección de envío'),('other','Otra dirección'),('private','Dirección Privada')])
    subtipo = fields.Selection([('Contacto comercial','Contacto comercial'),('Contacto sistemas','Contacto sistemas'),('Contacto para pagos','Contacto parra pagos'),('Contacto para compras','Contacto para compras'),('private','Dirección Privada')])
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
    direccionCiudad = fields.Char(string='Ciudad')
    direccionCodigoPostal = fields.Char(string='Código postal')
    direccionPais = fields.Many2one('res.country', store=True, string='País')
    direccionEstado = fields.Many2one('res.country.state', store=True, string='Estado', domain="[('country_id', '=?', direccionPais)]")
    
    direccionZona = fields.Selection([('SUR','SUR'),('NORTE','NORTE'),('PONIENTE','PONIENTE'),('ORIENTE','ORIENTE'),('CENTRO','CENTRO'),('DISTRIBUIDOR','DISTRIBUIDOR'),('MONTERREY','MONTERREY'),('CUERNAVACA','CUERNAVACA'),('GUADALAJARA','GUADALAJARA'),('QUERETARO','QUERETARO'),('CANCUN','CANCUN'),('VERACRUZ','VERACRUZ'),('PUEBLA','PUEBLA'),('TOLUCA','TOLUCA'),('LEON','LEON'),('COMODIN','COMODIN'),('VILLAHERMOSA','VILLAHERMOSA'),('MERIDA','MERIDA'),('ALTAMIRA','ALTAMIRA')])
    
    agregarContactoCheck = fields.Boolean(string="Añadir contacto", default=False)
    
    idLocalidadAyuda = fields.Integer(compute='_compute_id_localidad',string='Id Localidad Ayuda', store=False) 
    
    """
    seriesDeEquipoPorNumeroDeSerie = fields.Selection(_compute_series,compute='_compute_series',string='Series agregadas', store=False)
    
    @api.depends('x_studio_equipo_por_nmero_de_serie')
    def _compute_series(self):
        listaDeSeries = []
        for record in self:
            if len(record.x_studio_equipo_por_nmero_de_serie) > 0:
                for serie in record.x_studio_equipo_por_nmero_de_serie:
                    listaDeSerie.append((str(serie.name),str(serie.name)))
        return listaDeSerie
    """
    
    @api.depends('x_studio_empresas_relacionadas')
    def _compute_id_localidad(self):
        for record in self:
            record['idLocalidadAyuda'] = record.x_studio_empresas_relacionadas.id
        
        
    @api.onchange('x_studio_empresas_relacionadas')
    def cambiar_direccion_entrega(self):
        
        _logger.info("***************Que tiene en pedido de venta: " + str(self.x_studio_field_nO7Xg.id))
        _logger.info("**************** necesito ver que tiene =(" + str(self.x_studio_empresas_relacionadas.id))
        _logger.info("**************** self.id: " + str(self.id))
        _logger.info("**************** self.x_studio_ticket: " + str(self.x_studio_id_ticket))
        sale = self.x_studio_field_nO7Xg
        #if self.x_studio_field_nO7Xg != False and (self.x_studio_empresas_relacionadas.id == False or self.x_studio_empresas_relacionadas.id != None or len(str(self.x_studio_empresas_relacionadas.id)) != 0 or str(self.x_studio_empresas_relacionadas.id) is 0 or not str(self.x_studio_empresas_relacionadas.id) or self.x_studio_empresas_relacionadas.id != []) and self.x_studio_field_nO7Xg.state != 'sale':
        if self.x_studio_field_nO7Xg.id != False and self.x_studio_id_ticket != 0 and self.x_studio_field_nO7Xg.state != 'sale':
            _logger.info("****************solicitud: " + str(self.x_studio_field_nO7Xg.id))
            _logger.info("****************localidad: " + str(self.x_studio_empresas_relacionadas.id))
            
            if self.x_studio_field_nO7Xg.id != False:
                #self.env['sale.order'].write(['partner_shipping_id','=',''])
                self.env.cr.execute("update sale_order set partner_shipping_id = " + str(self.x_studio_empresas_relacionadas.id) + " where  id = " + str(sale.id) + ";")
                #raise Warning('Se cambio la dirreción de entrega del ticket: ' + str(self.id) + " dirección actualizada a: " + str(self.x_studio_empresas_relacionadas.name))
                #raise exceptions.Warning('Se cambio la dirreción de entrega del ticket: ' + str(self.x_studio_id_ticket) + " dirección actualizada a: " + str(self.x_studio_empresas_relacionadas.parent_id.name) + " " + str(self.x_studio_empresas_relacionadas.name))
                message = ('Se cambio la dirreción de entrega de la solicitud: ' + str(sale.name) + '  del ticket: ' + str(self.x_studio_id_ticket) + ". \nSe produjo el cambio al actualizar el campo 'Localidad'. \nLa dirección fue actualizada a: " + str(self.x_studio_empresas_relacionadas.parent_id.name) + " " + str(self.x_studio_empresas_relacionadas.name))
                mess= {
                        'title': _('Dirreción Actualizada!!!'),
                        'message' : message
                    }
                return {'warning': mess}
        else:
            if self.x_studio_id_ticket != 0 and self.x_studio_field_nO7Xg.id != False:
                raise exceptions.Warning('No se pudo actualizar la dirreción de la solicitud: ' + str(sale.name) + ' del ticket: ' + str(self.x_studio_id_ticket) + " debido a que ya fue validada la solicitud. \nIntento actualizar el campo 'Localidad' con la dirección: " + str(self.x_studio_empresas_relacionadas.parent_id.name) + " " + str(self.x_studio_empresas_relacionadas.name))
                
                
                
    
    def agregarContactoALocalidad(self):
        _logger.info("*****self.x_studio_empresas_relacionadas.id: " + str(self.x_studio_empresas_relacionadas.id))
        
        if self.x_studio_empresas_relacionadas.id != 0:
            contactoId = 0;
            #_logger.info("*******************************************self.nombreDelContacto: " + str(self.nombreDelContacto))
            titulo = ''
            if len(self.titulo) == 0: 
                titulo = '' 
            else: 
                titulo = self.titulo.id
                
            if self.tipoDeDireccion == "contact" and self.nombreDelContacto != False:
                contacto = self.sudo().env['res.partner'].create({'parent_id' : self.x_studio_empresas_relacionadas.id
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
                contacto = self.sudo().env['res.partner'].create({'parent_id' : self.x_studio_empresas_relacionadas.id
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
                contacto = self.sudo().env['res.partner'].create({'parent_id' : self.x_studio_empresas_relacionadas.id
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
                errorContactoSinNombre = "Contacto sin nombre"
                mensajeContactoSinNombre = "No es posible añadir un contacto sin nombre. Favor de indicar el nombre primero."
                raise exceptions.except_orm(_(errorContactoSinNombre), _(mensajeContactoSinNombre))
                
            self.env.cr.commit()
            if contactoId > 0:
                errorContactoGenerado = "Contacto agregado"
                mensajeContactoGenerado = "Contacto " + str(self.nombreDelContacto) + " agregado a la localidad " + str(self.x_studio_empresas_relacionadas.name)
                raise exceptions.except_orm(_(errorContactoGenerado), _(mensajeContactoGenerado))
                self.agregarContactoCheck = False
            else:
                errorContactoNoGenerado = "Contacto no agregado"
                mensajeContactoNoGenerado = "Contacto no agregado. Favor de verificar la información ingresada."
                raise exceptions.except_orm(_(errorContactoNoGenerado), _(mensajeContactoNoGenerado))
        else:
            errorContactoSinLocalidad = "Contacto sin localidad"
            mensajeContactoSinLocalidad = "No es posible añadir un contacto sin primero indicar la localidad. Favor de indicar la localidad primero."
            raise exceptions.except_orm(_(errorContactoSinLocalidad), _(mensajeContactoSinLocalidad))
    
    
    
    
    
    def _compute_difference(self):
        for rec in self:
            #rec.days_difference = (datetime.date.today()- rec.create_date).days   
            #fe = ''
            fecha = str(rec.create_date).split(' ')[0]
            _logger.info("***************t: " + str(fecha))
            #fe = t[0]
            converted_date = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
            #converted_date = datetime.datetime.strptime(str(rec.create_date), '%Y-%m-%d').date()
            rec.days_difference = (datetime.date.today() - converted_date).days
    
    
    #_logger.info("el id xD Toner xD")            

    #@api.model           
    #@api.depends('productosSolicitud')
    #@api.one
    """
    def _productos_solicitud_filtro(self):
        res = {}    
        e=''
        g=str(self.x_studio_nombretmp)
        list = ast.literal_eval(g)
        idf = self.team_id.id
        if idf == 8:
            _logger.info("el id xD Toner"+g)            
            e  = str([('categ_id', '=', 5),('x_studio_toner_compatible.id','in',list)])
        if idf == 9:
            _logger.info("el id xD Reffacciones"+g)
            e = str([('categ_id', '=', 7),('x_studio_toner_compatible.id','=',list[0])])
        #if idf != 9 and idf != 8:
        #    _logger.info("Compatibles xD"+g)
        #    res['domain']={'productosSolicitud':[('x_studio_toner_compatible.id','=',list[0])]}
        _logger.info(" res :"+str(e))    
        return e

    productosSolicitud = fields.Many2many('product.product', string="Productos Solicitados",domain=_productos_solicitud_filtro)
    """
    
    """
    #@api.depends('historialCuatro')
    @api.onchange('historialCuatro')
    def recuperaUltimaNota(self):
        #for record in self:
        historial = self.historialCuatro
        ultimaFila = len(historial) - 1
        if ultimaFila >= 0:
            self.x_studio_ultima_nota = str(historial[ultimaFila].x_disgnostico)
            self.x_studio_fecha_nota = str(historial[ultimaFila].create_date)
            self.x_studio_tecnico = str(historial[ultimaFila].x_persona)
    """
    
    """
    #@api.depends('historialCuatro')
    @api.onchange('historialCuatro')
    def recuperaUltimaNota(self):
        for record in self:
            historial = record.historialCuatro
            ultimaFila = len(historial) - 1
            if ultimaFila >= 0:
                record['x_studio_ultima_nota'] = str(historial[ultimaFila].x_disgnostico)
                record['x_studio_fecha_nota'] = str(historial[ultimaFila].create_date)
                record['x_studio_tecnico'] = str(historial[ultimaFila].x_persona)
    """                
    
    """
    @api.onchange('x_studio_equipo_por_nmero_de_serie')
    def anadirProductosATabla(self):
        
            Añade productos y el numero de serie que se agregaron al equipor 
            numero de serie a la tabla de productos. 
        
        _logger.info("anadirProductosATabla")
        if len(self.x_studio_equipo_por_nmero_de_serie) > 0:
            data = []
            for numeroDeSerie in self.x_studio_equipo_por_nmero_de_serie:
                data.append({'x_studio_currentuser': 
                           , 'categ_id': 
                           , '':
                            })
                str(numeroDeSerie.name)
                numeroDeSerie.x_studio_field_lMCjm.id
    """                
    
    
    
    
    @api.onchange('x_studio_generar_cambio')
    def genera_registro_contadores(self):
        _logger.info('Entrando a funcion genera_registro_contadores()')
        for record in self:
            if record.x_studio_generar_cambio == True:
                listaDeSeries = record.x_studio_equipo_por_nmero_de_serie
                for serie in listaDeSeries:
                    if serie.x_studio_cambiar == True:
                        contadorColor = serie.x_studio_contador_color
                        raise exceptions.ValidationError(str(contadorColor))
    
    """
    @api.onchange('x_studio_equipo_por_nmero_de_serie')
    def abierto(self):
        if self.x_studio_id_ticket:
            #raise exceptions.ValidationError("error gerardo")
            #if self.stage_id.name != 'Abierto':
            if self.stage_id.name == 'Pre-ticket':
                _logger.info("Id ticket: " + str(self.id))
                #query = "update helpdesk_ticket set stage_id = 89 where id = " + str(self.id) + ";"
                query = "update helpdesk_ticket set stage_id = 89 where id = " + str(self.x_studio_id_ticket) + ";"
                _logger.info("lol: " + query)
                ss = self.env.cr.execute(query)
                _logger.info("**********fun: abierto(), estado: " + str(self.stage_id.name))
                self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
                #self.env['x_historial_helpdesk'].create({'x_id_ticket':self.id ,'x_persona': self.env.user.name,'x_estado': "Abierto"})
    """
    
    estadoAbierto = fields.Boolean(string="Paso por estado abierto", default=False)
    
    @api.onchange('x_studio_equipo_por_nmero_de_serie')
    def abierto(self):
        if self.x_studio_id_ticket:
            _logger.info("------------------------self.stage_id.name: " + str(self.stage_id.name))
            _logger.info("------------------------self.x_studio_equipo_por_nmero_de_serie.id: " + str(self.x_studio_equipo_por_nmero_de_serie.id))
            estadoAntes = str(self.stage_id.name)
            if self.stage_id.name == 'Pre-ticket' and self.x_studio_equipo_por_nmero_de_serie.id != False and self.estadoAbierto == False:
            #if self.stage_id.name == 'Pre-ticket' and self.x_studio_equipo_por_nmero_de_serie.id != False and self.estadoAbierto == False:
                query = "update helpdesk_ticket set stage_id = 89 where id = " + str(self.x_studio_id_ticket) + ";"
                _logger.info("lol: " + query)
                ss = self.env.cr.execute(query)
                _logger.info("**********fun: abierto(), estado: " + str(self.stage_id.name))
                #self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
                self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': "Abierto"})
                message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Abierto' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                mess= {
                        'title': _('Estado de ticket actualizado!!!'),
                        'message' : message
                    }
                self.estadoAbierto = True
                return {'warning': mess}
    
    
    
    
    
    
    """
    @api.onchange('team_id')
    def asignacion(self):
        if self.x_studio_id_ticket:
            #raise exceptions.ValidationError("error gerardo")
            if self.stage_id.name != 'Asignado':
                query = "update helpdesk_ticket set stage_id = 2 where id = " + str(self.x_studio_id_ticket) + ";"
                _logger.info("lol: " + query)
                ss = self.env.cr.execute(query)             
                _logger.info("**********fun: asignacion(), estado: " + str(self.stage_id.name))                
                self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona':self.env.user.name ,'x_estado': "Asignado"})
        
        res = {}
        idEquipoDeAsistencia = self.team_id.id
        query = "select * from helpdesk_team_res_users_rel where helpdesk_team_id = " + str(idEquipoDeAsistencia) + ";"
        self.env.cr.execute(query)
        informacion = self.env.cr.fetchall()
        _logger.info("*********lol: " + str(informacion))
        listaUsuarios = []
        #res['domain']={'x_studio_productos':[('categ_id', '=', 5),('x_studio_toner_compatible.id','in',list)]}
        for idUsuario in informacion:
            _logger.info("*********idUsuario: " + str(idUsuario))
            listaUsuarios.append(idUsuario[1])
        _logger.info(str(listaUsuarios))
        dominio = [('id', 'in', listaUsuarios)]
        res['domain'] = {'user_id': dominio}
        return res
    """
    #Añadir al XML 
    estadoAsignacion = fields.Boolean(string="Paso por estado asignación", default=False)
    
    @api.onchange('team_id')
    def asignacion(self):
        _logger.info("-------------------------------------------------------------self.stage_id.name: " + str(self.stage_id.name))
        _logger.info("-------------------------------------------------------------team_id: " + str(self.team_id.id))
        if self.x_studio_id_ticket:
            estadoAntes = str(self.stage_id.name)
            #if self.stage_id.name == 'Abierto' and self.estadoAsignacion == False and self.team_id.id != False:
            if self.estadoAsignacion == False and self.team_id.id != False:
                query = "update helpdesk_ticket set stage_id = 2 where id = " + str(self.x_studio_id_ticket) + ";"
                _logger.info("lol: " + query)
                ss = self.env.cr.execute(query)             
                _logger.info("**********fun: asignacion(), estado: " + str(self.stage_id.name))                
                self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona':self.env.user.name ,'x_estado': "Asignado"})
                self.estadoAsignacion = True
                message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Asignado' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                mess= {
                        'title': _('Estado de ticket actualizado!!!'),
                        'message' : message
                    }
                
                res = {}
                idEquipoDeAsistencia = self.team_id.id
                query = "select * from helpdesk_team_res_users_rel where helpdesk_team_id = " + str(idEquipoDeAsistencia) + ";"
                self.env.cr.execute(query)
                informacion = self.env.cr.fetchall()
                _logger.info("*********lol: " + str(informacion))
                listaUsuarios = []
                #res['domain']={'x_studio_productos':[('categ_id', '=', 5),('x_studio_toner_compatible.id','in',list)]}
                for idUsuario in informacion:
                    _logger.info("*********idUsuario: " + str(idUsuario))
                    listaUsuarios.append(idUsuario[1])
                _logger.info(str(listaUsuarios))
                dominio = [('id', 'in', listaUsuarios)]
                
                return {'warning': mess, 'domain': {'user_id': dominio}}
            #else:
                #reasingado
                
        
        if self.team_id.id != False:
            res = {}
            idEquipoDeAsistencia = self.team_id.id
            query = "select * from helpdesk_team_res_users_rel where helpdesk_team_id = " + str(idEquipoDeAsistencia) + ";"
            self.env.cr.execute(query)
            informacion = self.env.cr.fetchall()
            _logger.info("*********lol: " + str(informacion))
            listaUsuarios = []
            #res['domain']={'x_studio_productos':[('categ_id', '=', 5),('x_studio_toner_compatible.id','in',list)]}
            for idUsuario in informacion:
                _logger.info("*********idUsuario: " + str(idUsuario))
                listaUsuarios.append(idUsuario[1])
            _logger.info(str(listaUsuarios))
            dominio = [('id', 'in', listaUsuarios)]
            res['domain'] = {'user_id': dominio}
            return res
    
    
    
    """
    @api.onchange('x_studio_tcnico')
    def cambioEstadoAtencion(self):
        if self.x_studio_id_ticket:
            #raise exceptions.ValidationError("error gerardo: " + str(self.stage_id.name))
            #if self.stage_id.name == 'Asignado' and self.stage_id.name != 'Atención':
            query = "update helpdesk_ticket set stage_id = 13 where id = " + str(self.x_studio_id_ticket) + ";"
            _logger.info("lol: " + query)
            ss = self.env.cr.execute(query)
            _logger.info("**********fun: cambioEstadoAtencion(), estado: " + str(self.stage_id.name))
            #self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
            self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.x_studio_tcnico.name,'x_estado': "Atención"})
    """
    
    
    #Añadir al XML 
    estadoAtencion = fields.Boolean(string="Paso por estado atención", default=False)
    
    @api.onchange('x_studio_tcnico')
    def cambioEstadoAtencion(self):
        _logger.info("-------------------------------------------------------------self.stage_id.name: " + str(self.stage_id.name))
        _logger.info("-------------------------------------------------------------self.x_studio_tcnico.id: " + str(self.x_studio_tcnico.id))
        if self.x_studio_id_ticket:
            estadoAntes = str(self.stage_id.name)
            if self.stage_id.name == 'Asignado' and self.x_studio_tcnico.id != False and self.estadoAtencion == False:
                query = "update helpdesk_ticket set stage_id = 13 where id = " + str(self.x_studio_id_ticket) + ";"
                _logger.info("lol: " + query)
                ss = self.env.cr.execute(query)
                _logger.info("**********fun: cambioEstadoAtencion(), estado: " + str(self.stage_id.name))
                #self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
                self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.x_studio_tcnico.name,'x_estado': "Atención"})
                message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Atención' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                mess= {
                        'title': _('Estado de ticket actualizado!!!'),
                        'message' : message
                    }
                self.estadoAtencion = True
                self.estadoResuelto = False
                return {'warning': mess}
    
    
    
    estadoResuelto = fields.Boolean(string="Paso por estado resuelto", default=False)
    
    #@api.onchange('stage_id')
    def cambioResuelto(self):
        #_logger.info("update current mode......................................")
        #if self.team_id == 8:
        #    if len(self.documentosTecnico)
        #if self.stage_id.name == 'Atención' and self.x_studio_productos != []:
        #raise exceptions.ValidationError("error gerardo: " + str(self.stage_id.name))
        estadoAntes = str(self.stage_id.name)
        if self.estadoResuelto == False:
            query = "update helpdesk_ticket set stage_id = 3 where id = " + str(self.x_studio_id_ticket) + ";"
            _logger.info("lol: " + query)
            ss = self.env.cr.execute(query)
            _logger.info("**********fun: cambioResuelto(), estado: " + str(self.stage_id.name))
            #self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
            self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': "Resuelto"})
            message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Resuelto' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
            mess= {
                    'title': _('Estado de ticket actualizado!!!'),
                    'message' : message
                }
            self.estadoResuelto = True
            self.estadoAtencion = False
            return {'warning': mess}

    estadoCotizacion = fields.Boolean(string="Paso por estado cotizacion", default=False)
    
    #@api.onchange('stage_id')
    def cambioCotizacion(self):
        estadoAntes = str(self.stage_id.name)
        #if self.stage_id.name == 'Cotización' and str(self.env.user.id) == str(self.x_studio_tcnico.user_id.id) and self.estadoCotizacion == False:
        #if str(self.env.user.id) == str(self.x_studio_tcnico.user_id.id) and self.estadoCotizacion == False:
        if self.estadoCotizacion == False:
            query = "update helpdesk_ticket set stage_id = 101 where id = " + str(self.x_studio_id_ticket) + ";"
            _logger.info("lol: " + query)
            ss = self.env.cr.execute(query)
            _logger.info("**********fun: cambioCotizacion(), estado: " + str(self.stage_id.name))
            #self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
            self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': "Cotización"})
            message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Cotización' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
            mess= {
                    'title': _('Estado de ticket actualizado!!!'),
                    'message' : message
                }
            self.estadoCotizacion = True
            return {'warning': mess}
            
     
    estadoResueltoPorDocTecnico = fields.Boolean(string="Paso por estado resuelto", default=False)
    #Falta comprobar
    @api.onchange('documentosTecnico')
    def cambioResueltoPorDocTecnico(self):
        #_logger.info("******************** type: " + str(type(self.documentosTecnico)))
        #_logger.info("********************self.documentosTecnico.id: " + str(self.documentosTecnico[0].id))
        _logger.info("********************self.env.user.id: " + str(self.env.user.id) + " **** self.x_studio_tcnico.user_id.id: " + str(self.x_studio_tcnico.user_id.id))
        #_logger.info("******************** type self.documentosTecnico.id: " + str(type(self.documentosTecnico)))
        estadoAntes = str(self.stage_id.name)
        #if self.documentosTecnico.id != False and str(self.env.user.id) == str(self.x_studio_tcnico.user_id.id):
        if str(self.env.user.id) == str(self.x_studio_tcnico.user_id.id) and self.estadoResueltoPorDocTecnico == False:
            query = "update helpdesk_ticket set stage_id = 3 where id = " + str(self.x_studio_id_ticket) + ";"
            _logger.info("lol: " + query)
            ss = self.env.cr.execute(query)
            _logger.info("**********fun: cambioResueltoPorDocTecnico(), estado: " + str(self.stage_id.name))
            #self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
            self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': "Resuelto"})
            message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Resuelto' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
            mess= {
                    'title': _('Estado de ticket actualizado!!!'),
                    'message' : message
                }
            self.estadoResueltoPorDocTecnico = True
            self.estadoAtencion = False
            return {'warning': mess}
            
            
    estadoCerrado = fields.Boolean(string="Paso por estado cerrado", default=False)
    #Falta comprobar
    #@api.onchange('stage_id')
    def cambioCerrado(self):
        estadoAntes = str(self.stage_id.name)
        #_logger.info("********************self.stage_id: " + str(self.stage_id))
        if self.stage_id.name == 'Resuelto' or self.stage_id.name == 'Abierto' or self.stage_id.name == 'Asignado' or self.stage_id.name == 'Atención' and self.estadoCerrado == False:
            query = "update helpdesk_ticket set stage_id = 18 where id = " + str(self.x_studio_id_ticket) + ";"
            _logger.info("lol: " + query)
            ss = self.env.cr.execute(query)
            _logger.info("**********fun: cambioCerrado(), estado: " + str(self.stage_id.name))
            #self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
            self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': "Cerrado"})
            message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Cerrado' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
            mess= {
                    'title': _('Estado de ticket actualizado!!!'),
                    'message' : message
                }
            self.estadoResueltoPorDocTecnico = True
            self.estadoAtencion = True
            return {'warning': mess}
    
    
    estadoCancelado = fields.Boolean(string="Paso por estado cancelado", default=False)
    #Falta comprobar
    #@api.onchange('stage_id')
    def cambioCancelado(self):
        estadoAntes = str(self.stage_id.name)
        #_logger.info("********************self.documentosTecnico.id: " + str(self.documentosTecnico.id))
        #if self.stage_id.name == 'Cancelado':
        if self.estadoCancelado == False:
            query = "update helpdesk_ticket set stage_id = 4 where id = " + str(self.x_studio_id_ticket) + ";"
            _logger.info("lol: " + query)
            ss = self.env.cr.execute(query)
            _logger.info("**********fun: cambioCancelado(), estado: " + str(self.stage_id.name))
            #self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
            self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': "Cancelado"})
            message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Cancelado' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
            mess= {
                    'title': _('Estado de ticket actualizado!!!'),
                    'message' : message
                }
            self.estadoCancelado = True
            return {'warning': mess}
    
    
    
    
    
            
    
    estadoSolicitudDeRefaccion = fields.Boolean(string="Paso por estado solicitud de refaccion", default=False)
    
    #@api.oncgange()
    @api.multi
    def crear_solicitud_refaccion(self):
        for record in self:
            #if record.x_studio_id_ticket != 0:
            if len(record.x_studio_productos) > 0:
                _logger.info("***********************************************************************************************" + str(self.x_studio_field_nO7Xg.state))
                if self.x_studio_field_nO7Xg.id != False and self.x_studio_field_nO7Xg.state != 'sale':
                    _logger.info("Entre en caso de que existe una solicitud y aun no ha sido validada")
                    sale = self.x_studio_field_nO7Xg
                    self.env.cr.execute("delete from sale_order_line where order_id = " + str(sale.id) +";")
                    for c in self.x_studio_productos:
                        self.env['sale.order.line'].create({'order_id' : sale.id
                                                          , 'product_id' : c.id
                                                          , 'product_uom_qty' : c.x_studio_cantidad_pedida
                                                          , 'x_studio_field_9nQhR':self.x_studio_equipo_por_nmero_de_serie[0].id
                                                          })
                        self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
                        #self.env.cr.commit()
                else:
                #if (record.x_studio_tipo_de_falla == 'Solicitud de refacción' ) or (record.x_studio_tipo_de_incidencia == 'Solicitud de refacción' ):
                    _logger.info("Entre en caso que no existe una solicitud y aun no ha sido validada")
                    sale = self.env['sale.order'].create({'partner_id' : record.partner_id.id
                                                                 , 'origin' : "Ticket de refacción: " + str(record.x_studio_id_ticket)
                                                                 , 'x_studio_tipo_de_solicitud' : 'Venta'
                                                                 , 'x_studio_requiere_instalacin' : True
                                                                 #, 'x_studio_fecha_y_hora_de_visita' : self.x_studio_rango_inicial_de_visita
                                                                 #, 'x_studio_field_rrhrN' : self.x_studio_rango_final_de_visita
                                                                 #, 'x_studio_comentarios_para_la_visita' : str(self.ticket_type_id.name)
                                                                 #, 'x_studio_field_bAsX8' : self.x_studio_prioridad
                                                                 #, 'commitment_date' : self.x_studio_rango_inicial_de_visita
                                                                 #, 'x_studio_fecha_final' : self.x_studio_rango_final_de_visita
                                                                 , 'x_studio_field_RnhKr': self.localidadContacto.id
                                                                 , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id
                                                                 , 'user_id' : record.user_id.id
                                                                 , 'x_studio_tcnico' : record.x_studio_tcnico.id
                                                                 , 'warehouse_id' : 5865   ##Id GENESIS AGRICOLA REFACCIONES  stock.warehouse
                                                                 , 'team_id' : 1})
                    _logger.info("********Venta creada, id: " + str(sale.id))
                    record['x_studio_field_nO7Xg'] = sale.id
                    for c in record.x_studio_productos:
                        self.env['sale.order.line'].create({'order_id' : sale.id
                                                                   , 'product_id' : c.id
                                                                   , 'product_uom_qty' : c.x_studio_cantidad_pedida
                                                                   ,'x_studio_field_9nQhR':self.x_studio_equipo_por_nmero_de_serie[0].id
                                                                   , 'price_unit': 0
                                                                  })
                        _logger.info("*****************solicitud id: " + str(sale.id) + " name solicitud: " + str(sale.name) + " cantidad pedida: " + str(c.x_studio_cantidad_pedida) + " Producto pedido: " + str(c.id) + " numero de serie: " + str(self.x_studio_equipo_por_nmero_de_serie[0].id) + " price unit: " + str(0))
                        sale.env['sale.order'].write({'x_studio_tipo_de_solicitud' : 'Venta'})
                        self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")



                    #if sale.id:
                    #    if self.x_studio_id_ticket:
                            #raise exceptions.ValidationError("error gerardo")
                            #if self.stage_id.name == 'Atención' and self.team_id.name == 'Equipo de hardware':
                    """
                    query = "update helpdesk_ticket set stage_id = 100 where id = " + str(self.x_studio_id_ticket) + ";"
                    _logger.info("lol: " + query)
                    ss = self.env.cr.execute(query)
                    _logger.info("**********fun: crear_solicitud_refaccion(), estado: " + str(self.stage_id.name))
                        #self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
                    self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': "Solicitud de refacción"})
                    """
                    
                saleTemp = self.x_studio_field_nO7Xg
                if saleTemp.id != False:
                    if self.x_studio_id_ticket:
                        estadoAntes = str(self.stage_id.name)
                        foraneoDistribuidor = 11
                        if (self.stage_id.name == 'Atención' or self.team_id.id == foraneoDistribuidor) and self.estadoSolicitudDeRefaccion == False:
                            query = "update helpdesk_ticket set stage_id = 100 where id = " + str(self.x_studio_id_ticket) + ";"
                            _logger.info("lol: " + query)
                            ss = self.env.cr.execute(query)
                            _logger.info("**********fun: crear_solicitud_refaccion(), estado: " + str(self.stage_id.name))
                                #self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
                            self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': "Solicitud de refacción"})
                            message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Solicitud de refacción' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                            mess= {
                                    'title': _('Estado de ticket actualizado!!!'),
                                    'message' : message
                                  }
                            self.estadoSolicitudDeRefaccion = True
                            return {'warning': mess}
                    
                    """
                    if self.team_id.name == 'Equipo de hardware':
                        query = "update helpdesk_ticket set stage_id = 100 where id = " + str(self.x_studio_id_ticket) + ";"
                        _logger.info("lol: " + query)
                        ss = self.env.cr.execute(query)
                        _logger.info("**********fun: crear_solicitud_refaccion(), estado: " + str(self.stage_id.name))
                        #self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
                        self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': "Solicitud de refacción"})
                    """
            
            #else:
            #    errorRefaccionNoGenerada = "Solicitud de refacción no generada"
            #    mensajeSolicitudRefaccionNoGenerada = "No es posible crear una solicitud de refacción sin guardar antes el ticket. Favor de guardar el ticket y posteriormente generar la solicitud"
            #    raise exceptions.except_orm(_(errorRefaccionNoGenerada), _(mensajeSolicitudRefaccionNoGenerada))
                
                
    #añadir XML
    estadoSolicitudDeRefaccionValidada = fields.Boolean(string="Paso por estado refaccion autorixada", default=False)
    
    #@api.onchange('x_studio_verificacin_de_refaccin')
    def validar_solicitud_refaccion(self):
        for record in self:
            sale = record.x_studio_field_nO7Xg
            if sale.id != 0:
                self.sudo().env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
                sale.write({'x_studio_tipo_de_solicitud' : 'Venta'})
                sale.action_confirm()
                
                
                estadoAntes = str(self.stage_id.name)
                if self.stage_id.name == 'Solicitud de refacción' and self.estadoSolicitudDeRefaccionValidada == False:
                    query = "update helpdesk_ticket set stage_id = 102 where id = " + str(self.x_studio_id_ticket) + ";"
                    _logger.info("lol: " + query)
                    ss = self.env.cr.execute(query)
                    self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': "Refacción Autorizada"})
                    
                    message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Refacción Autorizada' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                    mess= {
                            'title': _('Estado de ticket actualizado!!!'),
                            'message' : message
                          }
                    self.estadoSolicitudDeRefaccionValidada = True
                    return {'warning': mess}
                
            else:
                errorRefaccionNoValidada = "Solicitud de refacción no validada"
                mensajeSolicitudRefaccionNoValida = "No es posible validar una solicitud de refacción en el estado actual."
                estadoActual = str(record.stage_id.name)
                raise exceptions.except_orm(_(errorRefaccionNoValidada), _(mensajeSolicitudRefaccionNoValida + " Estado: " + estadoActual))
    
    
    
    """
    @api.onchange('x_studio_localidad_destino')
    def cambio(self):
      _logger.info('************* haciendo algo xD ' )
      for record in self:  
        if record.team_id.id == 76 :
            sale = self.env['stock.picking'].create({'partner_id' : record.partner_id.id
                                             #,'almacenOrigen':record.x_studio_empresas_relacionadas.id
                                             #,'almacenDestino':record.x_studio_field_yPznZ.id        
                                             ,'location_id':12
                                             ,'location_dest_id':16
                                             ,'scheduled_date': record.x_studio_fecha_prevista
                                             ,'picking_type_id': 5
                                            #, 'origin' : "Ticket de tóner: " + str(record.ticket_type_id.id)
                                            #, 'x_studio_tipo_de_solicitud' : "Venta"
                                            #, 'x_studio_requiere_instalacin' : True
                                                     
                                            #, 'user_id' : record.user_id.id                                           
                                            #, 'x_studio_tcnico' : record.x_studio_tcnico.id
                                            #, 'warehouse_id' : 1   ##Id GENESIS AGRICOLA REFACCIONES  stock.warehouse
                                            #, 'team_id' : 1      
                                          })
            _logger.info('************* haciendo algo xD '+str(sale.id) )
            record['x_studio_transferencia'] = sale.id
            
            for c in record.x_studio_equipo_por_nmero_de_serie:
             # _logger.info('*************cantidad a solicitar: ' + str(c.x_studio_cantidad_a_solicitar))
              self.env['stock.move'].create({'picking_id' : sale.id
                                            , 'product_id' : c.product_id.id
                                             ,'name':"test"
                                             ,'product_uom':1
                                             ,'location_id':1
                                             ,'location_dest_id':1
                                            #, 'product_uom_qty' : c.x_studio_cantidad_pedida
                                          })
    """        
    
    
    #@api.onchange('x_studio_captura_c')
    @api.multi
    def capturandoMesa(self):
      for record in self:  
            for c in record.x_studio_equipo_por_nmero_de_serie:
              _logger.info("lol: " + str(c.x_studio_field_A6PR9))
              if self.team_id.id==8:
                q='helpdesk.ticket'
              else:
                q='stock.production.lot'
              #if str(c.x_studio_field_A6PR9) =='Negro':
              if str(c.x_studio_color_bn) == 'B/N':
                  if int(c.x_studio_contador_bn_a_capturar) > int(c.x_studio_contador_bn):
                      
                      self.env['dcas.dcas'].create({'serie' : c.id
                                                    , 'contadorMono' : c.x_studio_contador_bn_a_capturar
                                                    , 'contadorColor' :c.x_studio_contador_color_a_capturar
                                                    ,'porcentajeNegro':c.x_studio__negro
                                                    ,'porcentajeCian':c.x_studio__cian      
                                                    ,'porcentajeAmarillo':c.x_studio__amarrillo      
                                                    ,'porcentajeMagenta':c.x_studio__magenta
                                                    ,'x_studio_descripcion':self.name
                                                    ,'x_studio_tickett':self.x_studio_id_ticket
                                                    ,'x_studio_hoja_de_estado':c.x_studio_evidencias
                                                    ,'x_studio_usuariocaptura':self.env.user.name
                                                    ,'fuente':q                                            
                                                  })                  
                      self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': 'captura ','x_disgnostico':'capturas :' + str('Mono'+str(c.x_studio_contador_bn_a_capturar)+', Color '+str(c.x_studio_contador_color_a_capturar)+', Amarillo '+str(c.x_studio__amarrillo)+', Cian '+str(c.x_studio__cian)+', Negro '+str(c.x_studio__negro)+', Magenta '+str(c.x_studio__magenta))})
                  else :
                    raise exceptions.ValidationError("Contador Monocromatico Menor")                     
              #if str(c.x_studio_field_A6PR9) != 'Negro':       
              if str(c.x_studio_color_bn) != 'B/N':
                  if int(c.x_studio_contador_color_a_capturar) > int(c.x_studio_contador_color) and int(c.x_studio_contador_bn_a_capturar) > int(c.x_studio_contador_bn):
                      self.env['dcas.dcas'].create({'serie' : c.id
                                                    , 'contadorMono' : c.x_studio_contador_bn_a_capturar
                                                    , 'contadorColor' :c.x_studio_contador_color_a_capturar
                                                    ,'porcentajeNegro':c.x_studio__negro
                                                    ,'porcentajeCian':c.x_studio__cian      
                                                    ,'porcentajeAmarillo':c.x_studio__amarrillo      
                                                    ,'porcentajeMagenta':c.x_studio__magenta
                                                    ,'x_studio_descripcion':self.name
                                                    ,'x_studio_tickett':self.x_studio_id_ticket
                                                    ,'x_studio_hoja_de_estado':c.x_studio_evidencias
                                                    ,'x_studio_usuariocaptura':self.env.user.name
                                                    ,'fuente':q                                            
                                                  })                  
                      self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': 'captura ','x_disgnostico':'capturas :' + str('Mono'+str(c.x_studio_contador_bn_a_capturar)+', Color '+str(c.x_studio_contador_color_a_capturar)+', Amarillo '+str(c.x_studio__amarrillo)+', Cian '+str(c.x_studio__cian)+', Negro '+str(c.x_studio__negro)+', Magenta '+str(c.x_studio__magenta))})
                  else :
                    raise exceptions.ValidationError("Error al capturar debe ser mayor")                                                 

                    
    estadoSolicitudDeToner = fields.Boolean(string="Paso por estado pendiente por autorizar solicitud", default=False)
    
    @api.onchange('x_studio_tipo_de_requerimiento')
    def toner(self):
      for record in self:
        _logger.info("***********************************************************************************************" + str(self.x_studio_field_nO7Xg.state))
        _logger.info("***********************************************************************************************" + str(self.x_studio_field_nO7Xg.id))
        if self.x_studio_field_nO7Xg.id != False and self.x_studio_field_nO7Xg.state != 'sale':
            _logger.info("Entre en caso de que existe una solicitud y aun no ha sido validada")
            sale = self.x_studio_field_nO7Xg
            self.env.cr.execute("delete from sale_order_line where order_id = " + str(sale.id) +";")
            for c in self.x_studio_productos:
                pro=self.env['product.product'].search([['name','=',c.id.name],['categ_id','=',5]])
                gen=pro.sorted(key='qty_available',reverse=True)[0]
                datos={'order_id' : sale.id, 'product_id' : gen.id, 'product_uom_qty' : c.x_studio_cantidad_pedida, 'x_studio_field_9nQhR':self.x_studio_equipo_por_nmero_de_serie[0].id}
                if(gen['qty_available']<=0):
                    datos['route_id']=1
                    datos['product_id']=c.id            
                self.env['sale.order.line'].create(datos)
                self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
                #self.env.cr.commit()
        else:
            #if record.x_studio_id_ticket != 0:
            _logger.info("Entre en caso que no existe una solicitud y aun no ha sido validada")
            if (record.team_id.id == 8 ) and record.x_studio_tipo_de_requerimiento == 'Tóner':
                sale = self.env['sale.order'].create({'partner_id' : record.partner_id.id
                                                , 'origin' : "Ticket de tóner: " + str(record.x_studio_id_ticket)
                                                , 'x_studio_tipo_de_solicitud' : "Venta"
                                                , 'x_studio_requiere_instalacin' : True                                       
                                                , 'user_id' : record.user_id.id                                           
                                                , 'x_studio_tcnico' : record.x_studio_tcnico.id
                                                , 'x_studio_field_RnhKr': self.localidadContacto.id
                                                , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id
                                                , 'warehouse_id' : 1   ##Id GENESIS AGRICOLA REFACCIONES  stock.warehouse
                                                , 'team_id' : 1
                                              })
                record['x_studio_field_nO7Xg'] = sale.id
                for c in record.x_studio_equipo_por_nmero_de_serie:
                    pro=self.env['product.product'].search([['name','=',c.x_studio_toner_compatible.name],['categ_id','=',5]])
                    gen=pro.sorted(key='qty_available',reverse=True)[0]
                    datos={'order_id' : sale.id, 'product_id' : c.x_studio_toner_compatible.id if(len(gen)==0) else gen.id, 'product_uom_qty' :1, 'x_studio_field_9nQhR': c.id , 'price_unit': 0}
                    if(gen['qty_available']<=0):
                        datos['route_id']=1
                        datos['product_id']=c.x_studio_toner_compatible.id
                    _logger.info('*************cantidad a solicitar: ' + str(c.id))
                    self.env['sale.order.line'].create(datos)
                    _logger.info("*****************solicitud id: " + str(sale.id) + " name solicitud: " + str(sale.name) + " cantidad pedida: " + str(1) + " Producto pedido: " + str(c.x_studio_toner_compatible.id if(len(gen)==0) else gen.id) + " price unit: " + str(0))
                    """  
                      self.env['dcas.dcas'].create({'serie' : c.id
                                                    , 'contadorMono' : c.x_studio_contador_bn_a_capturar
                                                    , 'contadorColor' :c.x_studio_contador_color_a_capturar
                                                    ,'porcentajeNegro':c.x_studio__negro
                                                    ,'porcentajeCian':c.x_studio__cian      
                                                    ,'porcentajeAmarillo':c.x_studio__amarrillo      
                                                    ,'porcentajeMagenta':c.x_studio__magenta
                                                    ,'x_studio_descripcion':self.name
                                                    ,'x_studio_tickett':self.x_studio_id_ticket
                                                    ,'x_studio_hoja_de_estado':c.x_studio_evidencias
                                                    ,'x_studio_usuariocaptura':self.env.user.name
                                                    ,'fuente':'helpdesk.ticket'

                                                  })


                      self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': 'captura ','x_disgnostico':'capturas :' + str('Mono'+str(c.x_studio_contador_bn_a_capturar)+', Color '+str(c.x_studio_contador_color_a_capturar)+', Amarillo '+str(c.x_studio__amarrillo)+', Cian '+str(c.x_studio__cian)+', Negro '+str(c.x_studio__negro)+', Magenta '+str(c.x_studio__magenta))})
                      """ 

                sale.env['sale.order'].write({'x_studio_tipo_de_solicitud' : 'Venta'})
                self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
            if (record.team_id.id == 13 ) and record.x_studio_tipo_de_requerimiento == 'Tóner':
                sale = self.env['sale.order'].create({'partner_id' : record.partner_id.id
                                                , 'origin' : "Ticket de tfs: " + str(record.x_studio_id_ticket)
                                                , 'x_studio_tipo_de_solicitud' : "Venta"
                                                , 'x_studio_requiere_instalacin' : True                                       
                                                , 'user_id' : record.user_id.id                                           
                                                , 'x_studio_tcnico' : record.x_studio_tcnico.id
                                                , 'x_studio_field_RnhKr': self.localidadContacto.id
                                                , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id
                                                , 'warehouse_id' : 1   ##Id GENESIS AGRICOLA REFACCIONES  stock.warehouse
                                                , 'team_id' : 1      
                                              })
                record['x_studio_field_nO7Xg'] = sale.id
                for c in record.x_studio_seriestoner:
                  #_logger.info('*************cantidad a solicitar: ' + str(c.x_studio_cantidad_a_solicitar))
                  self.env['sale.order.line'].create({'order_id' : sale.id
                                                , 'product_id' : c.id
                                                , 'product_uom_qty' : 1.0
                                                , 'x_studio_field_9nQhR' : self.env['stock.production.lot'].search([['name', '=', str(c.name)]]).id
                                              })
                sale.env['sale.order'].write({'x_studio_tipo_de_solicitud' : 'Venta'})
                self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")    

            saleTemp = self.x_studio_field_nO7Xg
            if saleTemp.id != False:
                if self.x_studio_id_ticket:
                    estadoAntes = str(self.stage_id.name)
                    #if self.stage_id.name == 'Atención' and self.estadoSolicitudDeToner == False:
                    if self.estadoSolicitudDeToner == False:    
                        query = "update helpdesk_ticket set stage_id = 91 where id = " + str(self.x_studio_id_ticket) + ";"
                        _logger.info("lol: " + query)
                        ss = self.env.cr.execute(query)
                        self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': "Pendiente por autorizar solicitud"})
                        message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Pendiente por autorizar solicitud' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                        mess= {
                                'title': _('Estado de ticket actualizado!!!'),
                                'message' : message
                              }
                        self.estadoSolicitudDeToner = True
                        return {'warning': mess}


            #else:
            #    errorTonerNoGenerada = "Solicitud de tóner no generada"
            #    mensajeSolicitudTonerNoGenerada = "No es posible crear una solicitud de tóner sin guardar antes el ticket. Favor de guardar el ticket y posteriormente generar la solicitud"
            #    raise exceptions.except_orm(_(errorTonerNoGenerada), _(mensajeSolicitudTonerNoGenerada))

        
        
        
        
    estadoSolicitudDeTonerValidar = fields.Boolean(string="Paso por estado autorizado y almacen", default=False)    
        
        
        
    #@api.onchange('x_studio_verificacin_de_tner')
    def validar_solicitud_toner(self):
        _logger.info("validar_solicitud_toner()")        
        for record in self:
            sale = record.x_studio_field_nO7Xg
            _logger.info("*******sale.id: " + str(sale.id))
            if sale.id != 0:
                self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
                sale.write({'x_studio_tipo_de_solicitud' : 'Venta'})
                sale.action_confirm()
                
                if self.estadoSolicitudDeTonerValidar == False:
                    query="update helpdesk_ticket set stage_id = 95 where id = " + str(self.x_studio_id_ticket) + ";" 
                    _logger.info("lol: " + query)
                    ss=self.env.cr.execute(query)
                    self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': "Autorizado"})

                    #En almacen
                    query="update helpdesk_ticket set stage_id = 93 where id = " + str(self.x_studio_id_ticket) + ";" 
                    _logger.info("lol: " + query)
                    ss=self.env.cr.execute(query)
                    self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': "En almacén"})

                    estadoAntes = str(self.stage_id.name)
                    message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Almacen' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                    mess= {
                            'title': _('Estado de ticket actualizado!!!'),
                            'message' : message
                          }
                    self.estadoSolicitudDeTonerValidar = True
                    return {'warning': mess}
                
            else:
                errorTonerNoValidado = "Solicitud de tóner no validada"
                mensajeSolicitudTonerNoValida = "No es posible validar una solicitud de tóner en el estado actual. Favor de verificar el estado del ticket o revisar que la solicitud se haya generado"
                estadoActual = str(record.stage_id.name)
                raise exceptions.except_orm(_(errorTonerNoValidado), _(mensajeSolicitudTonerNoValida + " Estado: " + estadoActual))
    
    @api.onchange('x_studio_desactivar_zona')
    def desactivar_datos_zona(self):
        res = {}
        if self.x_studio_desactivar_zona :
           res['domain']={'x_studio_responsable_de_equipo':[('x_studio_zona', '!=', False)]}
        return res
       
    #@api.model            
    @api.onchange('x_studio_activar_compatibilidad')
    #@api.multi
    def productos_filtro(self):
        res = {}             
        g = str(self.x_studio_nombretmp)
        
        if g !='False':
            list = ast.literal_eval(g)        
            idf = self.team_id.id
            tam = len(list)
            if idf == 8 or idf == 13 :
               _logger.info("el id xD Toner"+g)            
               res['domain']={'x_studio_productos':[('categ_id', '=', 5),('x_studio_toner_compatible.id','in',list)]}
            if idf == 9:
               _logger.info("el id xD Reffacciones"+g)
               res['domain']={'x_studio_productos':[('categ_id', '=', 7),('x_studio_toner_compatible.id','=',list[0])]}
            if idf != 9 and idf != 8:
               _logger.info("Compatibles xD" + g)
               res['domain']={'x_studio_productos':[('x_studio_toner_compatible.id','=',list[0])]}
               _logger.info("res"+str(res))
            #if idf 55:
            #   _logger.info("Cotizacion xD" + g)
            #   res['domain'] = {'x_studio_productos':[('x_studio_toner_compatible.id', '=', list[0]),('x_studio_toner_compatible.property_stock_inventory.id', '=', 121),('x_studio_toner_compatible.id property_stock_inventory.id', '=', 121)] }
            #   _logger.info("res"+str(res))
        return res
        
    @api.onchange('x_studio_zona')
    def actualiza_datos_zona_responsable_tecnico(self):
        res = {}
        #raise exceptions.ValidationError("test " + self.x_studio_zona)
        if self.x_studio_zona :
            res['domain']={'x_studio_tcnico':[('x_studio_zona', '=', self.x_studio_zona)]}
            #res['domain'] = {'x_studio_tcnico':['|',('x_studio_zona', '=', self.x_studio_zona),('x_studio_zona', '=', self.zona_estados)]}
        return res
    
    @api.onchange('x_studio_zona')
    def actualiza_datos_zona_responsable(self):
        res = {}
        #raise exceptions.ValidationError("test " + self.x_studio_zona)
        if self.x_studio_zona :
            res['domain']={'x_studio_responsable_de_equipo':[('x_studio_zona', '=', self.x_studio_zona)]}
        return res
   
   
   
    
    
    
    @api.onchange('stage_id')
    def actualiza_datos_estado(self):
        _logger.info("staged()  **********************************#*"+self.env.user.name)
        self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})        
    
    
    
    @api.onchange('x_studio_responsable_de_equipo')
    def actualiza_datos_zona_dos(self):
        s = self.stage_id.name
        #raise exceptions.ValidationError("No son vacios : "+str(s))
        res = self.x_studio_responsable_de_equipo.name
        team = self.team_id.name
        
        _logger.info("actualiza_datos_zona()  **********************************#*"+str(s)+" "+str(res)+""+str(team))
        if s=='Abierto' :
        #if s == 'New' :
            if self.x_studio_id_ticket :
               query="update helpdesk_ticket set stage_id = 2 where id = " + str(self.x_studio_id_ticket) + ";" 
               #raise exceptions.ValidationError("No son vacios : "+str(query))
               ss=self.env.cr.execute(query)
    """
    @api.onchange('x_studio_fecha_de_visita')
    def actualiza_datos_tecnico(self):
        s = self.stage_id.name
        #raise exceptions.ValidationError("No son vacios : "+str(s))
        if s=='Asignado' :
            if self.x_studio_tcnico :
               query="update helpdesk_ticket set stage_id = 3 where id = " + str(self.x_studio_id_ticket) + ";" 
               ss=self.env.cr.execute(query)
    """     
    """       
    @api.onchange('x_studio_tcnico')
    def actualiza_datos_zona(self):
        s = self.x_studio_tcnico.name
        b = self.stage_id.name
        self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': s,'x_estado': b })
    """
    
    @api.depends('x_studio_equipo_por_nmero_de_serie.x_studio_field_B7uLt')
    def obtener_contadores(self):        
        for record in self.x_studio_equipo_por_nmero_de_serie:
            if len(record)>0:
                f = record.x_studio_dcas_ultimo
                raise exceptions.ValidationError("No son vacios : "+str(f))
    
    
    #@api.one
    #@api.depends('team_id', 'x_studio_responsable_de_equipo')
    """
    @api.model
    @api.onchange('team_id', 'x_studio_responsable_de_equipo')
    def cambiar_seguidores(self):
        _logger.info("cambiar_github porfinV2   ***********************************()")
        _logger.info("cambiar_seguidores()")
        _logger.info("self._origin: " + str(self._origin) + ' self._origin.id: ' + str(self._origin.id))
        
        #https://www.odoo.com/es_ES/forum/ayuda-1/question/when-a-po-requires-approval-the-follower-of-the-warehouse-receipt-is-the-approver-i-need-it-to-be-the-user-who-created-the-po-136450
        #log(str(self.message_follower_ids), level='info')
        
        #self._origin.id
        
        ##Busanco subscriptores de modelo helpdesk con id especifico
        #log("id: " + str(record.x_studio_id_ticket), level='info')
        ids = self.env['mail.followers'].search_read(['&', ('res_model', '=', 'helpdesk.ticket'), ('res_id', '=',self.x_studio_id_ticket)], ['partner_id'])
        #log(str(ids), level='info')
        lista_followers_borrar = []
        id_cliente = self.partner_id.id
        #log('id_cliente: ' + str(id_cliente), level='info')
        for id_partner in ids:
            #log(str(id_partner['partner_id'][0]))
            id_guardar = id_partner['partner_id'][0]
            if id_guardar != id_cliente:
                #lista_followers_borrar.append(id_guardar)
                lista_followers_borrar.append(id_partner['id'])
            
        #log(str(lista_followers_borrar), level='info')


        #record.message_subscribe([9978])

        # Diamel Luna Chavelas
        id_test = 826   #Id de Diamel Luna Chavelas
        id_test_res_partner = 10528  #Id de res_partner.name = Test


        equipo_de_atencion_al_cliente = 1
        equipo_de_almacen = 2
        equipo_de_distribucion = 3
        equipo_de_finanzas = 4
        equipo_de_hardware = 5
        equipo_de_lecturas = 6
        equipo_de_sistemas = 7
        equipo_de_toner = 8


        responsable_atencion_al_cliente = id_test
        responsable_equipo_de_toner = id_test
        responsable_equipo_de_sistemas = id_test
        responsable_equipo_de_hardware = id_test
        responsable_equipo_de_finanzas = id_test
        responsable_equipo_de_lecturas = id_test
        responsable_equipo_de_distribucion = id_test
        responsable_equipo_de_almacen = id_test

        x_studio_responsable_de_equipo = 'x_studio_responsable_de_equipo'


        ## Por cada caso añadir el id de cada responsable de equipo y modificar para añadir a estos
        ## al seguimiento de los ticket's
        subscritor_temporal = id_test_res_partner


        #record.write({'x_studio_responsable_de_equipo' : responsable_atencion_al_cliente})


        equipo = self.team_id.id

        if equipo == equipo_de_atencion_al_cliente:
            _logger.info("Entrando a if equipo_de_atencion_al_cliente.............................................................. " )
            
            unsubs = False
            for follower in self.message_follower_ids:    
                #record.message_unsubscribe([follower.partner_id.id])
                for follower_borrar in lista_followers_borrar:
                    #log(str(follower.id), level = 'info')
                    #log(str(follower_borrar), level = 'info')
                    if follower_borrar == follower.id:
                        #log(str([follower.partner_id.id]), level = 'info')
                        #log('entro if:', level = 'info')
                        _logger.info('partner_ids: ' + str(follower.partner_id.id) + ' ' + str(follower.partner_id.name))
                        #unsubs = self._origin.sudo().message_unsubscribe(partner_ids = list([follower.partner_id.id]), channel_ids = None)
                        
                        #unsubs = self.sudo().message_unsubscribe_users(partner_ids = [follower.partner_id.id])
                        
                        unsubs = self.env.cr.execute("delete from mail_followers where res_model='helpdesk.ticket' and res_id=" + str(self.x_studio_id_ticket) + " and partner_id=" +  str(follower.partner_id.id) + ";")
                        
                        
                        _logger.info('Unsubs: ' + str(unsubs))
            
            
            #record.message_subscribe([responsable_atencion_al_cliente])                           ##Añade seguidores
            #self._origin.id
            
            regresa = self._origin.sudo()._message_subscribe(partner_ids=[subscritor_temporal], channel_ids=None, subtype_ids=None)
            
            #regresa = self.env.cr.execute("insert into mail_followers (res_model, res_id, partner_id) values ('helpdesk.ticket', " + str(self._origin.id) + ", " +  str(subscritor_temporal) + ");")
            
            self._origin.sudo().write({x_studio_responsable_de_equipo : responsable_atencion_al_cliente})      ##Asigna responsable de equipo
            _logger.info("regresa: " + str(regresa))
            _logger.info("Saliendo de if equipo_de_atencion_al_cliente............................................................. ")
            
          
          
        if equipo == equipo_de_toner:
            
            _logger.info("Entrando a if equipo_de_toner.............................................................. " )
            
            unsubs = False
            for follower in self.message_follower_ids:    
                #record.message_unsubscribe([follower.partner_id.id])
                for follower_borrar in lista_followers_borrar:
                    #log(str(follower.id), level = 'info')
                    #log(str(follower_borrar), level = 'info')
                    if follower_borrar == follower.id:
                        #log(str([follower.partner_id.id]), level = 'info')
                        #log('entro if:', level = 'info')
                        _logger.info('partner_ids: ' + str(follower.partner_id.id) + ' ' + str(follower.partner_id.name))
                        #unsubs = self._origin.sudo().message_unsubscribe(partner_ids = list([follower.partner_id.id]), channel_ids = None)
                        
                        #unsubs = self.sudo().message_unsubscribe_users(partner_ids = [follower.partner_id.id])
                        
                        unsubs = self.env.cr.execute("delete from mail_followers where res_model='helpdesk.ticket' and res_id=" + str(self.x_studio_id_ticket) + " and partner_id=" +  str(follower.partner_id.id) + ";")
                        
                        
                        _logger.info('Unsubs: ' + str(unsubs))
            
              
        
            #record.message_subscribe([responsable_equipo_de_toner])
            regresa = self._origin.sudo()._message_subscribe(partner_ids=[subscritor_temporal], channel_ids=None, subtype_ids=None)
            #regresa = self.env.cr.execute("insert into mail_followers (res_model, res_id, partner_id) values ('helpdesk.ticket', " + str(self._origin.id) + ", " +  str(subscritor_temporal) + ");")
            _logger.info("regresa: " + str(regresa))
            self._origin.sudo().write({x_studio_responsable_de_equipo : responsable_equipo_de_toner})
            
            _logger.info("Saliendo de if equipo_de_toner............................................................. ")
          

        if equipo == equipo_de_sistemas:
            _logger.info("Entrando a if equipo_de_sistemas.............................................................. " )
            
            unsubs = False
            for follower in self.message_follower_ids:    
                #record.message_unsubscribe([follower.partner_id.id])
                for follower_borrar in lista_followers_borrar:
                    #log(str(follower.id), level = 'info')
                    #log(str(follower_borrar), level = 'info')
                    if follower_borrar == follower.id:
                        #log(str([follower.partner_id.id]), level = 'info')
                        #log('entro if:', level = 'info')
                        _logger.info('partner_ids: ' + str(follower.partner_id.id) + ' ' + str(follower.partner_id.name))
                        #unsubs = self._origin.sudo().message_unsubscribe(partner_ids = list([follower.partner_id.id]), channel_ids = None)
                        
                        #unsubs = self.sudo().message_unsubscribe_users(partner_ids = [follower.partner_id.id])
                        
                        unsubs = self.env.cr.execute("delete from mail_followers where res_model='helpdesk.ticket' and res_id=" + str(self.x_studio_id_ticket) + " and partner_id=" +  str(follower.partner_id.id) + ";")
                        
                        
                        _logger.info('Unsubs: ' + str(unsubs))
            
            #record.message_subscribe([responsable_equipo_de_sistemas])
            regresa = self._origin.sudo()._message_subscribe(partner_ids=[subscritor_temporal], channel_ids=None, subtype_ids=None)
            #regresa = self.env.cr.execute("insert into mail_followers (res_model, res_id, partner_id) values ('helpdesk.ticket', " + str(self._origin.id) + ", " +  str(subscritor_temporal) + ");")
            _logger.info("regresa: " + str(regresa))
            self._origin.sudo().write({x_studio_responsable_de_equipo : responsable_equipo_de_sistemas})
            
            _logger.info("Saliendo de if equipo_de_sistemas............................................................. ")
          
          
        if equipo == equipo_de_hardware:
            _logger.info("Entrando a if equipo_de_hardware.............................................................. " )
            
            unsubs = False
            for follower in self.message_follower_ids:    
                #record.message_unsubscribe([follower.partner_id.id])
                for follower_borrar in lista_followers_borrar:
                    #log(str(follower.id), level = 'info')
                    #log(str(follower_borrar), level = 'info')
                    if follower_borrar == follower.id:
                        #log(str([follower.partner_id.id]), level = 'info')
                        #log('entro if:', level = 'info')
                        _logger.info('partner_ids: ' + str(follower.partner_id.id) + ' ' + str(follower.partner_id.name))
                        #unsubs = self._origin.sudo().message_unsubscribe(partner_ids = list([follower.partner_id.id]), channel_ids = None)
                        
                        #unsubs = self.sudo().message_unsubscribe_users(partner_ids = [follower.partner_id.id])
                        
                        unsubs = self.env.cr.execute("delete from mail_followers where res_model='helpdesk.ticket' and res_id=" + str(self.x_studio_id_ticket) + " and partner_id=" +  str(follower.partner_id.id) + ";")
                        
                        
                        _logger.info('Unsubs: ' + str(unsubs))
            
            #record.message_subscribe([responsable_equipo_de_hardware])
            regresa = self._origin.sudo()._message_subscribe(partner_ids=[subscritor_temporal], channel_ids=None, subtype_ids=None)
            #regresa = self.env.cr.execute("insert into mail_followers (res_model, res_id, partner_id) values ('helpdesk.ticket', " + str(self._origin.id) + ", " +  str(subscritor_temporal) + ");")
            _logger.info("regresa: " + str(regresa))
            self._origin.sudo().write({x_studio_responsable_de_equipo : responsable_equipo_de_hardware})
            _logger.info("Saliendo de if equipo_de_hardware............................................................. ")
          

        if equipo == equipo_de_finanzas:
            _logger.info("Entrando a if equipo_de_finanzas.............................................................. " )
            
            unsubs = False
            for follower in self.message_follower_ids:    
                #record.message_unsubscribe([follower.partner_id.id])
                for follower_borrar in lista_followers_borrar:
                    #log(str(follower.id), level = 'info')
                    #log(str(follower_borrar), level = 'info')
                    if follower_borrar == follower.id:
                        #log(str([follower.partner_id.id]), level = 'info')
                        #log('entro if:', level = 'info')
                        _logger.info('partner_ids: ' + str(follower.partner_id.id) + ' ' + str(follower.partner_id.name))
                        #unsubs = self._origin.sudo().message_unsubscribe(partner_ids = list([follower.partner_id.id]), channel_ids = None)
                        
                        #unsubs = self.sudo().message_unsubscribe_users(partner_ids = [follower.partner_id.id])
                        
                        unsubs = self.env.cr.execute("delete from mail_followers where res_model='helpdesk.ticket' and res_id=" + str(self.x_studio_id_ticket) + " and partner_id=" +  str(follower.partner_id.id) + ";")
                        
                        
                        _logger.info('Unsubs: ' + str(unsubs))
            
            #record.message_subscribe([responsable_equipo_de_finanzas])
            regresa = self._origin.sudo()._message_subscribe(partner_ids=[subscritor_temporal], channel_ids=None, subtype_ids=None)
            #regresa = self.env.cr.execute("insert into mail_followers (res_model, res_id, partner_id) values ('helpdesk.ticket', " + str(self._origin.id) + ", " +  str(subscritor_temporal) + ");")
            _logger.info("regresa: " + str(regresa))
            self._origin.sudo().write({x_studio_responsable_de_equipo : responsable_equipo_de_finanzas})
            _logger.info("Saliendo de if equipo_de_finanzas............................................................. ")
          
        if equipo == equipo_de_lecturas:
            _logger.info("Entrando a if equipo_de_lecturas.............................................................. " )
            
            unsubs = False
            for follower in self.message_follower_ids:    
                #record.message_unsubscribe([follower.partner_id.id])
                for follower_borrar in lista_followers_borrar:
                    #log(str(follower.id), level = 'info')
                    #log(str(follower_borrar), level = 'info')
                    if follower_borrar == follower.id:
                        #log(str([follower.partner_id.id]), level = 'info')
                        #log('entro if:', level = 'info')
                        _logger.info('partner_ids: ' + str(follower.partner_id.id) + ' ' + str(follower.partner_id.name))
                        #unsubs = self._origin.sudo().message_unsubscribe(partner_ids = list([follower.partner_id.id]), channel_ids = None)
                        
                        #unsubs = self.sudo().message_unsubscribe_users(partner_ids = [follower.partner_id.id])
                        
                        unsubs = self.env.cr.execute("delete from mail_followers where res_model='helpdesk.ticket' and res_id=" + str(self.x_studio_id_ticket) + " and partner_id=" +  str(follower.partner_id.id) + ";")
                        
                        
                        _logger.info('Unsubs: ' + str(unsubs))
            
            #record.message_subscribe([responsable_equipo_de_lecturas])
            regresa = self._origin.sudo()._message_subscribe(partner_ids=[subscritor_temporal], channel_ids=None, subtype_ids=None)
            #regresa = self.env.cr.execute("insert into mail_followers (res_model, res_id, partner_id) values ('helpdesk.ticket', " + str(self._origin.id) + ", " +  str(subscritor_temporal) + ");")
            _logger.info("regresa: " + str(regresa))
            self._origin.sudo().write({x_studio_responsable_de_equipo : responsable_equipo_de_lecturas})
            _logger.info("Saliendo de if equipo_de_lecturas............................................................. ")
          

        if equipo == equipo_de_distribucion:
            _logger.info("Entrando a if equipo_de_distribucion.............................................................. " )
            
            unsubs = False
            for follower in self.message_follower_ids:    
                #record.message_unsubscribe([follower.partner_id.id])
                for follower_borrar in lista_followers_borrar:
                    #log(str(follower.id), level = 'info')
                    #log(str(follower_borrar), level = 'info')
                    if follower_borrar == follower.id:
                        #log(str([follower.partner_id.id]), level = 'info')
                        #log('entro if:', level = 'info')
                        _logger.info('partner_ids: ' + str(follower.partner_id.id) + ' ' + str(follower.partner_id.name))
                        #unsubs = self._origin.sudo().message_unsubscribe(partner_ids = list([follower.partner_id.id]), channel_ids = None)
                        
                        #unsubs = self.sudo().message_unsubscribe_users(partner_ids = [follower.partner_id.id])
                        
                        unsubs = self.env.cr.execute("delete from mail_followers where res_model='helpdesk.ticket' and res_id=" + str(self.x_studio_id_ticket) + " and partner_id=" +  str(follower.partner_id.id) + ";")
                        
                        
                        _logger.info('Unsubs: ' + str(unsubs))
            
            #record.message_subscribe([responsable_equipo_de_distribucion])
            regresa = self._origin.sudo()._message_subscribe(partner_ids=[subscritor_temporal], channel_ids=None, subtype_ids=None)
            #regresa = self.env.cr.execute("insert into mail_followers (res_model, res_id, partner_id) values ('helpdesk.ticket', " + str(self._origin.id) + ", " +  str(subscritor_temporal) + ");")
            _logger.info("regresa: " + str(regresa))
            self._origin.sudo().write({x_studio_responsable_de_equipo : responsable_equipo_de_distribucion})
            _logger.info("Saliendo de if equipo_de_distribucion............................................................. ")
          

        if equipo == equipo_de_almacen:
            _logger.info("Entrando a if equipo_de_almacen............................................................................ ")
            #id del seguidor(marco)
            #ids_partner =11
            
            
            #for r in self.message_follower_ids:
             #   if(r.partner_id.id!=7219):
              #      ids_partner.append(r.partner_id.id)
               #     _logger.info('hi'+str(r.partner_id.id))
            #self['message_follower_ids']=[(3,11,0)]
            #hasta que se guarda borra el registro
            
            #self.env.cr.execute("delete from mail_followers where res_model='helpdesk.ticket' and res_id="+str(self.x_studio_id_ticket)+" and partner_id="+str(ids_partner)+";")
            
            #self['message_follower_ids']=[(6,0,ids_partner)]
            #unsubs = self.message_unsubscribe(partner_ids = [826], channel_ids = None)
            #unsubs=self.env['mail.followers'].sudo().search([('res_model', '=','helpdesk.ticket'),('res_id', '=', self.x_studio_id_ticket),('partner_id', '=', 826)]).unlink()
            #_logger.info('Unsubs: ' + str('hola')+str(self.x_studio_id_ticket))
            
            
            #raise Warning('Entrando a if equipo_de_almacen... ')
            #log("Entrando a if equipo_de_almacen... ", level='info')
            #unsubs = record.sudo().message_unsubscribe(lista_followers_borrar)
            unsubs = False
            for follower in self.message_follower_ids:    
                #record.message_unsubscribe([follower.partner_id.id])
                for follower_borrar in lista_followers_borrar:
                    #log(str(follower.id), level = 'info')
                    #log(str(follower_borrar), level = 'info')
                    if follower_borrar == follower.id:
                        #log(str([follower.partner_id.id]), level = 'info')
                        #log('entro if:', level = 'info')
                        _logger.info('partner_ids: ' + str(follower.partner_id.id) + ' ' + str(follower.partner_id.name))
                        #unsubs = self._origin.sudo().message_unsubscribe(partner_ids = list([follower.partner_id.id]), channel_ids = None)
                        
                        #unsubs = self.sudo().message_unsubscribe_users(partner_ids = [follower.partner_id.id])
                        
                        unsubs = self.env.cr.execute("delete from mail_followers where res_model='helpdesk.ticket' and res_id=" + str(self.x_studio_id_ticket) + " and partner_id=" +  str(follower.partner_id.id) + ";")
                        
                        
                        _logger.info('Unsubs: ' + str(unsubs))
            
            
            
            #record.message_subscribe([responsable_equipo_de_almacen])
            regresa = self._origin.sudo()._message_subscribe(partner_ids=[subscritor_temporal], channel_ids=None, subtype_ids=None)
            #regresa = self.env.cr.execute("insert into mail_followers (res_model, res_id, partner_id) values ('helpdesk.ticket', " + str(self._origin.id) + ", " +  str(subscritor_temporal) + ");")
            _logger.info("regresa: " + str(regresa))
            
            self._origin.sudo().write({x_studio_responsable_de_equipo : responsable_equipo_de_almacen})
            _logger.info('Saliendo de if equipo_de_almacen................................................................................. unsubs = ' + str(unsubs))
    """
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    @api.onchange('partner_id', 'x_studio_empresas_relacionadas')
    def actualiza_dominio_en_numeros_de_serie(self):
        for record in self:
            zero = 0
            dominio = []
            #for record in self:
            id_cliente = record.partner_id.id
            #id_cliente = record.x_studio_id_cliente
            id_localidad = record.x_studio_empresas_relacionadas.id

            record['x_studio_id_cliente'] = id_cliente# + " , " + str(id_cliente)
            record['x_studio_filtro_numeros_de_serie'] = id_localidad

            if id_cliente != zero:
              #raise Warning('entro1')
              dominio = ['&', ('x_studio_categoria_de_producto_3.name','=','Equipo'), ('x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id', '=', id_cliente)]
                
            else:
              #raise Warning('entro2')
              dominio = [('x_studio_categoria_de_producto_3.name','=','Equipo')]
              record['partner_name'] = ''
              record['partner_email'] = ''
              record['x_studio_nivel_del_cliente'] = ''
              record['x_studio_telefono'] = ''
              record['x_studio_movil'] = ''
              record['x_studio_empresas_relacionadas'] = ''
              if self.team_id.id==8:
                 record['x_studio_equipo_por_nmero_de_serie'] = ''
              if self.team_id.id!=8:
                 record['x_studio_equipo_por_nmero_de_serie'] = ''   

            if id_cliente != zero  and id_localidad != zero:
              #raise Warning('entro3')
              dominio = ['&', '&', ('x_studio_categoria_de_producto_3.name','=','Equipo'), ('x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id', '=', id_cliente),('x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.id','=',id_localidad)]

            if id_localidad == zero and id_cliente != zero:
              #raise Warning('entro4')
              dominio = ['&', ('x_studio_categoria_de_producto_3.name','=','Equipo'), ('x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id', '=', id_cliente)]

            if id_cliente == zero and id_localidad == zero:
              #raise Warning('entro5')
              dominio = [('x_studio_categoria_de_producto_3.name','=','Equipo')]
              record['partner_name'] = ''
              record['partner_email'] = ''
              record['x_studio_nivel_del_cliente'] = ''
              record['x_studio_telefono'] = ''
              record['x_studio_movil'] = ''
            if self.team_id.id==8:
               action = {'domain':{'x_studio_equipo_por_nmero_de_serie':dominio}}
            if self.team_id.id!=8:
               action = {'domain':{'x_studio_equipo_por_nmero_de_serie':dominio}}    
            return action
    
    
    #@api.model
    #@api.multi
    @api.onchange('x_studio_equipo_por_nmero_de_serie')
    #@api.depends('x_studio_equipo_por_nmero_de_serie')
    def actualiza_datos_cliente(self):        
        if int(self.x_studio_tamao_lista) > 0 and self.team_id.id != 8:
            _logger.info("actualiza_datos_cliente()" + str(self.x_studio_equipo_por_nmero_de_serie[0].id))
            query="select h.id from helpdesk_ticket_stock_production_lot_rel s, helpdesk_ticket h where h.id=s.helpdesk_ticket_id and h.id!="+str(self.x_studio_id_ticket)+"  and h.stage_id!=18 and h.team_id!=8 and  h.active='t' and stock_production_lot_id = "+str(self.x_studio_equipo_por_nmero_de_serie[0].id)+" limit 1;"            
            _logger.info("primera query s "+str(query))
            self.env.cr.execute(query)                        
            informacion = self.env.cr.fetchall()
            if len(informacion) > 0:
                raise exceptions.ValidationError("No es posible registrar número de serie, primero cerrar el ticket con el id  "+str(informacion[0][0]))
        if int(self.x_studio_tamao_lista) > 0 and self.team_id.id == 8:
            _logger.info("actualiza_datos_cliente()" + str(self.x_studio_equipo_por_nmero_de_serie[0].id))
            queryt="select h.id from helpdesk_ticket_stock_production_lot_rel s, helpdesk_ticket h where h.id=s.helpdesk_ticket_id and h.id!="+str(self.x_studio_id_ticket)+"  and h.stage_id!=18 and h.team_id=8 and  h.active='t' and stock_production_lot_id = "+str(self.x_studio_equipo_por_nmero_de_serie[0].id)+" limit 1;"            
            _logger.info("primera query st "+str(queryt))
            self.env.cr.execute(queryt)                        
            informaciont = self.env.cr.fetchall()
            if len(informaciont) > 0:
                message = ('Estas agregando una serie de un ticket ya en proceso en equipo de toner. \n Ticket: '+str(informaciont[0][0]))
                mess= {
                        'title': _('Alerta!!!'),
                        'message' : message
                              }
                return {'warning': mess}                                        
        """
        if int(self.x_studio_tamao_lista) > 0 and self.team_id.id != 8:
           _logger.info("actualiza_datos_cliente()"+str(self.x_studio_equipo_por_nmero_de_serie[0].id))
           query = "select * from helpdesk_ticket_stock_production_lot_rel where stock_production_lot_id  = " + str(self.x_studio_equipo_por_nmero_de_serie[0].id) + " limit 1;"
           self.env.cr.execute(query)
           informacion = self.env.cr.fetchall()
           if len(informacion) > 0:
                _logger.info("************************ticketTemporalInformacion: " + str(informacion))
                #ticketTemporal = self.env['helpdesk.ticket'].search(['id', '=', str(informacion[0][0])])
                #_logger.info("************************ticketTemporal: " + str(ticketTemporal))
                #_logger.info("************************ticketTemporal.x_studio_nmero_de_serie: " + str(ticketTemporal.x_studio_nmero_de_serie))
                
                #if ticketTemporal.x_studio_nmero_de_serie:
                queryD = "select stage_id,id from helpdesk_ticket where id = " + str(informacion[0][0]) + " and active != 'f' and team_id = " + str(self.team_id.id) +" limit 1;"
                self.env.cr.execute(queryD)
                informacionD = self.env.cr.fetchall()
                _logger.info()
                if len(informacionD) > 0 and str(informacionD[0][1]) != str(self.x_studio_id_ticket):
                    _logger.info("actualiza_datos_cliente2()  "+str(informacionD) +'  '+ str(informacion))
                    _logger.info("actualiza_datos_cliente3()  "+str(self.x_studio_equipo_por_nmero_de_serie[0].id) +'18=='+ str(informacionD[0][0]))
                    _logger.info("aaa"+' '+str(self.x_studio_equipo_por_nmero_de_serie[0].id)+'=='+str(informacion[0][1]) +'and'+ str(informacionD[0][0]) +'==18')
                    if int(self.x_studio_equipo_por_nmero_de_serie[0].id) == int(informacion[0][1]) and int(informacionD[0][0]) != 18 :
                        raise exceptions.ValidationError("No es posible registrar número de serie, primero cerrar el ticket con el id  "+str(informacionD[0][1]))
        """             
           

        
        _logger.info("self._origin: " + str(self._origin) + ' self._origin.id: ' + str(self._origin.id))
        
        v = {}
        ids = []
        localidad = []
        _logger.info("self el tamaño: "+str(self.x_studio_tamao_lista))
        for record in self:
            cantidad_numeros_serie = record.x_studio_tamao_lista
           # _logger.info("******************team_id: "+ str(record.team_id.id) + " cantidad_numeros_serie: "+ str(cantidad_numeros_serie))
            if record.team_id.id!=8:
                    if  int(cantidad_numeros_serie) < 2 :
                        _logger.info('record_ 1: ' + str(self._origin.partner_id))
                        _logger.info('record_id 1: ' + str(self._origin.id))
                        _my_object = self.env['helpdesk.ticket']
                        #v['x_studio_equipo_por_nmero_de_serie'] = {record.x_studio_equipo_por_nmero_de_serie.id}


                        #_logger.info('record_feliz : ' + str(record.x_studio_equipo_por_nmero_de_serie.id))
                        #ids.append(record.x_studio_equipo_por_nmero_de_serie.id)

                        #record['x_studio_equipo_por_nmero_de_serie'] = [(4,record.x_studio_equipo_por_nmero_de_serie.id)]


                        _logger.info('*********x_studio_equipo_por_nmero_de_serie: ')
                        _logger.info(str(record.x_studio_equipo_por_nmero_de_serie))
                        for numeros_serie in record.x_studio_equipo_por_nmero_de_serie:
                            ids.append(numeros_serie.id)
                            _logger.info('record_ 2: ' + str(self._origin))
                            _logger.info("Numeros_serie")
                            _logger.info(numeros_serie.name)
                            for move_line in numeros_serie.x_studio_move_line:
                                _logger.info('record_ 3: ' + str(self._origin))
                                _logger.info("move line")
                                #move_line.para.almacen.ubicacion.
                                _logger.info('Cliente info***************************************************************************')
                                _logger.info(move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id)
                                cliente = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id
                                self._origin.sudo().write({'partner_id' : cliente})
                                record.partner_id = cliente
                                idM=self._origin.id
                                _logger.info("que show"+str(idM))
                                if cliente == []:
                                    self.env.cr.execute("update helpdesk_ticket set partner_id = " + cliente + "  where  id = " + idM + ";")
                                v['partner_id'] = cliente
                                _logger.info(move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.phone)
                                cliente_telefono = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.phone
                                self._origin.sudo().write({'x_studio_telefono' : cliente_telefono})
                                record.x_studio_telefono = cliente_telefono
                                if cliente_telefono != []:
                                    srtt="update helpdesk_ticket set x_studio_telefono = '" + str(cliente_telefono) + "' where  id = " + str(idM) + ";"
                                    _logger.info("update gacho"+srtt)
                                    #s=self.env.cr.execute("update helpdesk_ticket set x_studio_telefono = '" + str(cliente_telefono) + "' where  id = " + str(idM) + ";")
                                    #_logger.info("update gacho 2 "+str(s))
                                v['x_studio_telefono'] = cliente_telefono
                                _logger.info(move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.mobile)
                                cliente_movil = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.mobile
                                self._origin.sudo().write({'x_studio_movil' : cliente_movil})
                                record.x_studio_movil = cliente_movil
                                if cliente_movil == []:
                                    self.env.cr.execute("update helpdesk_ticket set x_studio_movil = '" + str(cliente_movil) + "' where  id = " +idM + ";")
                                v['x_studio_movil'] = cliente_movil
                                _logger.info(move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.x_studio_nivel_del_cliente)
                                cliente_nivel = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.x_studio_nivel_del_cliente
                                self._origin.sudo().write({'x_studio_nivel_del_cliente' : cliente_nivel})
                                record.x_studio_nivel_del_cliente = cliente_nivel
                                if cliente_nivel == []:
                                    self.env.cr.execute("update helpdesk_ticket set x_studio_nivel_del_cliente = '" + str(cliente_nivel) + "' where  id = " + idM + ";")
                                v['x_studio_nivel_del_cliente'] = cliente_nivel

                                #localidad datos
                                _logger.info('Localidad info*************************************************************************')
                                _logger.info(move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z)
                                localidad = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.id
                                _logger.info('localidad id: ' + str(localidad))
                                self._origin.sudo().write({'x_studio_empresas_relacionadas' : localidad})
                                record.x_studio_empresas_relacionadas = localidad

                                _logger.info(move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.phone)
                                #telefono_localidad = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.phone
                                #self._origin.sudo().write({x_studio_telefono_localidad : telefono_localidad})
                                _logger.info(move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.mobile)
                                #movil_localidad = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.mobile
                                #self._origin.sudo().write({x_studio_movil_localidad : movil_localidad})
                                _logger.info(move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.email)
                                #email_localidad = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.email
                                #self._origin.sudo().write({x_studio_correo_electrnico_de_localidad : email_localidad})

                                #
                                #_logger.info(move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.)

                            #self._origin.sudo().write({x_studio_responsable_de_equipo : responsable_equipo_de_distribucion})

                            #_logger.info(record['x_studio_equipo_por_nmero_de_serie'])
                            _logger.info(ids)
                            #record['x_studio_equipo_por_nmero_de_serie'] = (6, 0, [ids])
                            #record.sudo().write({x_studio_equipo_por_nmero_de_serie : [(6, 0, [ids])] })
                            #self._origin.sudo().write({'x_studio_equipo_por_nmero_de_serie' : (4, ids) })
                            lista_ids = []
                            for id in ids:
                                lista_ids.append((4,id))
                            #v['x_studio_equipo_por_nmero_de_serie'] = [(4, ids[0]), (4, ids[1])]
                            v['x_studio_equipo_por_nmero_de_serie'] = lista_ids
                            self._origin.sudo().write({'x_studio_equipo_por_nmero_de_serie' : lista_ids})
                            record.x_studio_equipo_por_nmero_de_serie = lista_ids
                            """
                            if localidad != []:
                                srtt="update helpdesk_ticket set x_studio_empresas_relacionadas = " + str(localidad) + " where  id = " + str(idM )+ ";"
                                _logger.info("update gacho localidad " + srtt)
                                record.x_studio_empresas_relacionadas = localidad
                                record['x_studio_empresas_relacionadas'] = localidad
                                self.env.cr.execute(srtt)
                                #self.env.cr.commit()
                                v['x_studio_empresas_relacionadas'] = localidad        
                            """
                            _logger.info({'value': v})
                            _logger.info(v)
                            #self._origin.env['helpdesk.ticket'].sudo().write(v)

                            #res = super(helpdesk_update, self).sudo().write(v)
                            #return res
                            #return {'value': v}        
                    else:
                        raise exceptions.ValidationError("No es posible registrar más de un número de serie")
            if record.team_id.id==8:
                _logger.info('record_ 1: ' + str(self._origin.partner_id))
                _logger.info('record_id 1: ' + str(self._origin.id))
                _my_object = self.env['helpdesk.ticket']
                #v['x_studio_equipo_por_nmero_de_serie'] = {record.x_studio_equipo_por_nmero_de_serie.id}


                #_logger.info('record_feliz : ' + str(record.x_studio_equipo_por_nmero_de_serie.id))
                #ids.append(record.x_studio_equipo_por_nmero_de_serie.id)

                #record['x_studio_equipo_por_nmero_de_serie'] = [(4,record.x_studio_equipo_por_nmero_de_serie.id)]


                _logger.info('*********order_line: ')
                _logger.info(str(record.x_studio_equipo_por_nmero_de_serie))
                for numeros_serie in record.x_studio_equipo_por_nmero_de_serie:
                    ids.append(numeros_serie.id)
                    _logger.info('record_ 2: ' + str(self._origin))
                    _logger.info("Numeros_serie "+str(numeros_serie.id))
                    _logger.info(numeros_serie.name)
                    for move_line in numeros_serie.x_studio_move_line:
                        _logger.info('record_ 3: ' + str(self._origin))
                        _logger.info("move line")
                        #move_line.para.almacen.ubicacion.
                        _logger.info('Cliente info***************************************************************************')
                        _logger.info(move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id)
                        cliente = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id
                        self._origin.sudo().write({'partner_id' : cliente})
                        record.partner_id = cliente
                        idM=self._origin.id
                        _logger.info("que show"+str(idM))
                        if cliente == []:
                            self.env.cr.execute("update helpdesk_ticket set partner_id = " + cliente + "  where  id = " + idM + ";")
                        v['partner_id'] = cliente
                        _logger.info(move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.phone)
                        cliente_telefono = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.phone
                        self._origin.sudo().write({'x_studio_telefono' : cliente_telefono})
                        record.x_studio_telefono = cliente_telefono
                        if cliente_telefono != []:
                            srtt="update helpdesk_ticket set x_studio_telefono = '" + str(cliente_telefono) + "' where  id = " + str(idM) + ";"
                            _logger.info("update gacho"+srtt)
                            #s=self.env.cr.execute("update helpdesk_ticket set x_studio_telefono = '" + str(cliente_telefono) + "' where  id = " + str(idM) + ";")
                            #_logger.info("update gacho 2 "+str(s))
                        v['x_studio_telefono'] = cliente_telefono
                        _logger.info(move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.mobile)
                        cliente_movil = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.mobile
                        self._origin.sudo().write({'x_studio_movil' : cliente_movil})
                        record.x_studio_movil = cliente_movil
                        if cliente_movil == []:
                            self.env.cr.execute("update helpdesk_ticket set x_studio_movil = '" + str(cliente_movil) + "' where  id = " +idM + ";")
                        v['x_studio_movil'] = cliente_movil
                        _logger.info(move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.x_studio_nivel_del_cliente)
                        cliente_nivel = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.x_studio_nivel_del_cliente
                        self._origin.sudo().write({'x_studio_nivel_del_cliente' : cliente_nivel})
                        record.x_studio_nivel_del_cliente = cliente_nivel
                        if cliente_nivel == []:
                            self.env.cr.execute("update helpdesk_ticket set x_studio_nivel_del_cliente = '" + str(cliente_nivel) + "' where  id = " + idM + ";")
                        v['x_studio_nivel_del_cliente'] = cliente_nivel

                        #localidad datos
                        _logger.info('Localidad info*************************************************************************')
                        _logger.info(move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z)
                        localidad = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.id
                        _logger.info('localidad id: ' + str(localidad))
                        self._origin.sudo().write({'x_studio_empresas_relacionadas' : localidad})
                        record.x_studio_empresas_relacionadas = localidad

                        _logger.info(move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.phone)
                        #telefono_localidad = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.phone
                        #self._origin.sudo().write({x_studio_telefono_localidad : telefono_localidad})
                        _logger.info(move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.mobile)
                        #movil_localidad = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.mobile
                        #self._origin.sudo().write({x_studio_movil_localidad : movil_localidad})
                        _logger.info(move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.email)
                        #email_localidad = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.email
                        #self._origin.sudo().write({x_studio_correo_electrnico_de_localidad : email_localidad})

                        #
                        #_logger.info(move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.)

                    #self._origin.sudo().write({x_studio_responsable_de_equipo : responsable_equipo_de_distribucion})

                    #_logger.info(record['x_studio_equipo_por_nmero_de_serie'])
                    _logger.info(ids)
                    #record['x_studio_equipo_por_nmero_de_serie'] = (6, 0, [ids])
                    #record.sudo().write({x_studio_equipo_por_nmero_de_serie : [(6, 0, [ids])] })
                    #self._origin.sudo().write({'x_studio_equipo_por_nmero_de_serie' : (4, ids) })
                    lista_ids = []
                    for id in ids:
                        lista_ids.append((4,id))
                    #v['x_studio_equipo_por_nmero_de_serie'] = [(4, ids[0]), (4, ids[1])]
                    v['x_studio_equipo_por_nmero_de_serie'] = lista_ids
                    self._origin.sudo().write({'x_studio_equipo_por_nmero_de_serie' : lista_ids})
                    record.x_studio_equipo_por_nmero_de_serie = lista_ids
                    """
                    if localidad != []:
                        srtt="update helpdesk_ticket set x_studio_empresas_relacionadas = " + str(localidad) + " where  id = " + str(idM )+ ";"
                        _logger.info("update gacho localidad " + srtt)
                        record.x_studio_empresas_relacionadas = localidad
                        record['x_studio_empresas_relacionadas'] = localidad
                        self.env.cr.execute(srtt)
                        #self.env.cr.commit()
                        v['x_studio_empresas_relacionadas'] = localidad        
                    """
                    _logger.info({'value': v})
                    _logger.info(v)
                    #self._origin.env['helpdesk.ticket'].sudo().write(v)

                    #res = super(helpdesk_update, self).sudo().write(v)
                    #return res
                    #return {'value': v}
                
            
    

                
    """
    @api.model
    def create(self, vals):
        _logger.info('create() +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        _logger.info("self._origin: " + str(self._origin) + ' self._origin.id: ' + str(self._origin.id))
        if vals.get('team_id'):
            vals.update(item for item in self._onchange_team_get_values(self.env['helpdesk.team'].browse(vals['team_id'])).items() if item[0] not in vals)
        if 'partner_id' in vals and 'partner_email' not in vals:
            partner_email = self.env['res.partner'].browse(vals['partner_id']).email
            vals.update(partner_email=partner_email)
        # Manually create a partner now since 'generate_recipients' doesn't keep the name. This is
        # to avoid intrusive changes in the 'mail' module
        if 'partner_name' in vals and 'partner_email' in vals and 'partner_id' not in vals:
            vals['partner_id'] = self.env['res.partner'].find_or_create(
                formataddr((vals['partner_name'], vals['partner_email']))
            )

        # context: no_log, because subtype already handle this
        ticket = super(HelpdeskTicket, self.with_context(mail_create_nolog=True)).create(vals)
        if ticket.partner_id:
            ticket.message_subscribe(partner_ids=ticket.partner_id.ids)
            ticket._onchange_partner_id()
        if ticket.user_id:
            ticket.assign_date = ticket.create_date
            ticket.assign_hours = 0
        
        
        
        
        
        #record.message_subscribe([9978])
        #raise Warning('entro')
        # Diamel Luna Chavelas
        id_test = 826   #Id de Diamel Luna Chavelas
        id_test_res_partner = 7804



        equipo_de_atencion_al_cliente = 1
        equipo_de_almacen = 2
        equipo_de_distribucion = 3
        equipo_de_finanzas = 4
        equipo_de_hardware = 5
        equipo_de_lecturas = 6
        equipo_de_sistemas = 7
        equipo_de_toner = 8


        responsable_atencion_al_cliente = id_test
        responsable_equipo_de_toner = id_test
        responsable_equipo_de_sistemas = id_test
        responsable_equipo_de_hardware = id_test
        responsable_equipo_de_finanzas = id_test
        responsable_equipo_de_lecturas = id_test
        responsable_equipo_de_distribucion = id_test
        responsable_equipo_de_almacen = id_test

        x_studio_responsable_de_equipo = 'x_studio_responsable_de_equipo'


        ## Por cada caso añadir el id de cada responsable de equipo y modificar para añadir a estos
        ## al seguimiento de los ticket's
        subscritor_temporal = id_test_res_partner


        #record.write({'x_studio_responsable_de_equipo' : responsable_atencion_al_cliente})


        equipo = self.team_id.id

        if equipo == equipo_de_atencion_al_cliente:
            _logger.info('entro a equipo_de_atencion_al_cliente')
            #record.message_subscribe([responsable_atencion_al_cliente])                           ##Añade seguidores
            self.message_subscribe([subscritor_temporal])
            self.write({x_studio_responsable_de_equipo : responsable_atencion_al_cliente})      ##Asigna responsable de equipo

        if equipo == equipo_de_toner:
            _logger.info('entro a equipo_de_toner')
            #record.message_subscribe([responsable_equipo_de_toner])
            self.message_subscribe([subscritor_temporal])
            self.write({x_studio_responsable_de_equipo : responsable_equipo_de_toner})

        if equipo == equipo_de_sistemas:
            _logger.info('entro a equipo_de_sistemas')
            #record.message_subscribe([responsable_equipo_de_sistemas])
            self.message_subscribe([subscritor_temporal])
            self.write({x_studio_responsable_de_equipo : responsable_equipo_de_sistemas})

        if equipo == equipo_de_hardware:
            _logger.info('entro a equipo_de_hardware')
            #record.message_subscribe([responsable_equipo_de_hardware])
            self.message_subscribe([subscritor_temporal])
            self.write({x_studio_responsable_de_equipo : responsable_equipo_de_hardware})

        if equipo == equipo_de_finanzas:
            _logger.info('entro a equipo_de_finanzas')
            #record.message_subscribe([responsable_equipo_de_finanzas])
            self.message_subscribe([subscritor_temporal])
            self.write({x_studio_responsable_de_equipo : responsable_equipo_de_finanzas})

        if equipo == equipo_de_lecturas:
            _logger.info('entro a equipo_de_lecturas')
            #record.message_subscribe([responsable_equipo_de_lecturas])
            self.message_subscribe([subscritor_temporal])
            self.write({x_studio_responsable_de_equipo : responsable_equipo_de_lecturas})

        if equipo == equipo_de_distribucion:
            _logger.info('entro a equipo_de_distribucion')
            #record.message_subscribe([responsable_equipo_de_distribucion])
            self.message_subscribe([subscritor_temporal])
            self.write({x_studio_responsable_de_equipo : responsable_equipo_de_distribucion})

        if equipo == equipo_de_almacen:
            _logger.info('entro a equipo_de_almacen')
            #record.message_subscribe([responsable_equipo_de_almacen])
            self.message_subscribe([subscritor_temporal])
            self.write({x_studio_responsable_de_equipo : responsable_equipo_de_almacen})
        
        
        
        return ticket
    """
    @api.model
    def message_new(self, msg, custom_values=None):
        values = dict(custom_values or {}, partner_email=msg.get('from'), partner_id=msg.get('author_id'))

        _logger.info('************ticket: ' + str(msg.get('from')))
        if(("gnsys.mx" in str(msg.get('from'))) or ("scgenesis.mx" in str(msg.get('from')))):
            return 0
        ticket = super(helpdesk_update, self).message_new(msg, custom_values=values)

        partner_ids = [x for x in ticket._find_partner_from_emails(self._ticket_email_split(msg)) if x]
        customer_ids = ticket._find_partner_from_emails(tools.email_split(values['partner_email']))
        partner_ids += customer_ids

        if customer_ids and not values.get('partner_id'):
            ticket.partner_id = customer_ids[0]
        if partner_ids:
            ticket.message_subscribe(partner_ids)
        return ticket
   
    """
    @api.multi
    @api.depends('create_date')
    def calcularDiasAtraso(self):
        _logger.info("***************calcularDiasAtraso()")
        for record in self:
            _logger.info("***************record.create_date: " + str(record.create_date))
            if record.create_date:
                d = 0
                fe = ''
                t = str(r.create_date).split(' ')
                _logger.info("***************t: " + str(t))
                fe = t[0].split('-')
                _logger.info("***************fe: " + str(fe))
                x = datetime.datetime(2020, 1, 8)
                _logger.info("***************x: " + str(x))
                y = datetime.datetime(int(fe[0]), int(fe[1]), int(fe[2]))
                _logger.info("***************y: " + str(y))
                z = x - y
                _logger.info("***************z: " + str(z))
                z = str(z).split(' days')
                _logger.info("***************z: " + str(z))
                d = int(z[0])
                _logger.info("***************d: " + str(d))
                r['x_studio_das_de_atraso'] = fe
    """            
    
    
    """
    @api.onchange('historialCuatro')
    def recuperaUltimaNota(self):
        _logger.info("*****************recuperaUltimaNota()")
        #for record in self:
        historial = self.historialCuatro
        _logger.info("*****************historial: " + str(historial))
        ultimaFila = len(historial) - 1
        _logger.info("*****************ultimaFila: " + str(ultimaFila))
        if ultimaFila >= 0:
            _logger.info("*****************Entre if ultimaFila >= 0:")
            self.x_studio_ultima_nota = str(historial[ultimaFila].x_disgnostico)
            _logger.info("*****************self.x_studio_ultima_nota: " + str(self.x_studio_ultima_nota))
            self.x_studio_fecha_nota = str(historial[ultimaFila].create_date)
            _logger.info("*****************self.x_studio_fecha_nota: " + str(self.x_studio_fecha_nota))
            self.x_studio_tecnico = str(historial[ultimaFila].x_persona)
            _logger.info("*****************self.x_studio_tecnico: " + str(self.x_studio_tecnico)
    """
   
    order_line = fields.One2many('helpdesk.lines','ticket',string='Order Lines')
class helpdesk_lines(models.Model):
    _name="helpdesk.lines"
    _description = "Ticket Order"
    producto=fields.Many2one('product.product')
    cantidad=fields.Integer(string='Cantidad')
    serie=fields.Many2one('stock.production.lot')
    ticket=fields.Many2one('helpdesk.ticket',string='Order Reference')
    contadorAnterior=fields.Many2one('dcas.dcas',string='Anterior',compute='ultimoContador')
    contadorColor=fields.Integer(string='Contador Color')
    contadorNegro=fields.Integer(string='Contador Monocromatico')
    usuarioCaptura=fields.Char(string='Capturado por:') 
    current_user = fields.Many2one('res.users','Current User', default=lambda self: self.env.user)
    
    
    
    aA=fields.Integer(related='contadorAnterior.porcentajeAmarillo',string='Porcentaje A Amarillo')
    a=fields.Integer(string=' Porcentaje Amarillo')
    c=fields.Integer(string='Porcentaje Cian')
    cA=fields.Integer(related='contadorAnterior.porcentajeCian',string='Porcentaje A Cian')
    nA=fields.Integer(related='contadorAnterior.porcentajeNegro',string='Porcentaje A Negro')
    n=fields.Integer(string='Porcentaje Negro')
    m=fields.Integer(string='Porcentaje Magenta')
    mA=fields.Integer(related='contadorAnterior.porcentajeMagenta',string='Porcentaje A Magenta')
    
    
    
    contadorAnteriorMono=fields.Integer(related='contadorAnterior.contadorMono',string='Anterior Monocromatico')
    contadorAnteriorColor=fields.Integer(related='contadorAnterior.contadorColor',string='Anterior Color')
    impresiones=fields.Integer(related='serie.x_studio_impresiones',string='Impresiones B/N')
    impresionesColor=fields.Integer(related='serie.x_studio_impresiones_color',string='Impresiones Color')
    colorToner=fields.Char(related='serie.x_studio_field_A6PR9',string='Color Toner')
    area=fields.Integer()
    

    @api.depends('serie')
    def ultimoContador(self):
        for record in self:
            j=0
            for dc in record.serie.dca:
                if(j==0):
                    record['contadorAnterior']=dc.id
                    j=j+1
                    
    @api.onchange('serie')
    def productos_filtro(self):
        res = {}
        d=[]
        for p in self.serie.product_id.x_studio_toner_compatible:
            d.append(p.id)
        if self.serie !='False':   
            idf = self.area
            if idf == 8 or idf == 13 :          
               res['domain']={'producto':[('categ_id', '=', 5),('id','in',d)]}
            if idf == 9:
               res['domain']={'producto':[('categ_id', '=', 7),('id','in',d)]}
            if idf != 9 and idf != 8:
               res['domain']={'producto':[('id','in',d)]}
        return res

    
    
    
    
