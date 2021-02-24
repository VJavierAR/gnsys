# -*- coding: utf-8 -*-

from odoo import _, models, fields, api, tools
from email.utils import formataddr
from odoo.exceptions import UserError
from odoo import exceptions
import logging, ast
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
    
    
    @api.onchange('x_studio_equipo_por_nmero_de_serie')
    def abierto(self):
        if self.x_studio_id_ticket:
            #raise exceptions.ValidationError("error gerardo")
            if self.stage_id.name != 'Abierto':
                query = "update helpdesk_ticket set stage_id = 89 where id = " + str(self.x_studio_id_ticket) + ";"
                _logger.info("lol: " + query)
                ss = self.env.cr.execute(query)
                self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})

    
    @api.onchange('team_id')
    def asignacion(self):
        if self.x_studio_id_ticket:
            #raise exceptions.ValidationError("error gerardo")
            if self.stage_id.name != 'Asignado':
                query = "update helpdesk_ticket set stage_id = 2 where id = " + str(self.x_studio_id_ticket) + ";"
                _logger.info("lol: " + query)
                ss = self.env.cr.execute(query)
                self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
    
    
    @api.onchange('x_studio_tcnico')
    def cambioEstadoAtencion(self):
        if self.x_studio_id_ticket:
            #raise exceptions.ValidationError("error gerardo: " + str(self.stage_id.name))
            if self.stage_id.name == 'Asignado' and self.stage_id.name != 'Atención':
                query = "update helpdesk_ticket set stage_id = 13 where id = " + str(self.x_studio_id_ticket) + ";"
                _logger.info("lol: " + query)
                ss = self.env.cr.execute(query)
                self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
        
    
    @api.onchange('stage_id')
    def cambioResuelto(self):
        #_logger.info("update current mode......................................")
        if self.stage_id.name == 'Atención' and self.x_studio_productos != []:
            #raise exceptions.ValidationError("error gerardo: " + str(self.stage_id.name))
            query = "update helpdesk_ticket set stage_id = 3 where id = " + str(self.x_studio_id_ticket) + ";"
            _logger.info("lol: " + query)
            ss = self.env.cr.execute(query)
            self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
    

    
    @api.onchange('stage_id')
    def cambioCotizacion(self):
        if self.stage_id.name == 'Cotización' and str(self.env.user.id) == str(self.x_studio_tcnico.user_id.id):
            query = "update helpdesk_ticket set stage_id = 101 where id = " + str(self.x_studio_id_ticket) + ";"
            _logger.info("lol: " + query)
            ss = self.env.cr.execute(query)
            self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
    
    #Falta comprobar
    """
    @api.onchange('x_studio_prueba')
    def cambioRefaccionParaEntregar(self):
        _logger.info("************x_studio_prueba: " + str(self.x_studio_prueba))
        if self.x_studio_prueba == 'distribución':
            query = "update helpdesk_ticket set stage_id = 103 where id = " + str(self.x_studio_id_ticket) + ";"
            _logger.info("lol: " + query)
            ss = self.env.cr.execute(query)
            self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
    """
    
    #Falta comprobar
    @api.onchange('documentosTecnico')
    def cambioResueltoPorDocTecnico(self):
        #_logger.info("********************self.documentosTecnico.id: " + str(self.documentosTecnico.id))
        if self.documentosTecnico.id != False and str(self.env.user.id) == str(self.x_studio_tcnico.user_id.id):
            query = "update helpdesk_ticket set stage_id = 3 where id = " + str(self.x_studio_id_ticket) + ";"
            _logger.info("lol: " + query)
            ss = self.env.cr.execute(query)
            self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
        
    #Falta comprobar
    @api.onchange('stage_id')
    def cambioCerrado(self):
        #_logger.info("********************self.stage_id: " + str(self.stage_id))
        if self.stage_id.name == 'Cerrado':
            query = "update helpdesk_ticket set stage_id = 18 where id = " + str(self.x_studio_id_ticket) + ";"
            _logger.info("lol: " + query)
            ss = self.env.cr.execute(query)
            self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
    
    #Falta comprobar
    @api.onchange('stage_id')
    def cambioCancelado(self):
        #_logger.info("********************self.documentosTecnico.id: " + str(self.documentosTecnico.id))
        if self.stage_id.name == 'Cancelado':
            query = "update helpdesk_ticket set stage_id = 4 where id = " + str(self.x_studio_id_ticket) + ";"
            _logger.info("lol: " + query)
            ss = self.env.cr.execute(query)
            self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
    
    
    
    
    
            
    
    
    
    
    @api.onchange('x_studio_tipo_de_falla','x_studio_tipo_de_incidencia')
    def crear_solicitud_refaccion(self):
        self.ensure_one()
        if  (self.x_studio_tipo_de_falla == 'Solicitud de refacción' ) or (self.x_studio_tipo_de_incidencia == 'Solicitud de refacción' ) :                
            sale = self.sudo().env['sale.order'].create({'partner_id' : self.partner_id.id
                                                         , 'origin' : "Ticket de refacción: " + str(self.x_studio_id_ticket)
                                                         , 'x_studio_tipo_de_solicitud' : 'Venta'
                                                         , 'x_studio_requiere_instalacin' : True
                                                         #, 'x_studio_fecha_y_hora_de_visita' : self.x_studio_rango_inicial_de_visita
                                                         #, 'x_studio_field_rrhrN' : self.x_studio_rango_final_de_visita
                                                         #, 'x_studio_comentarios_para_la_visita' : str(self.ticket_type_id.name)
                                                         #, 'x_studio_field_bAsX8' : self.x_studio_prioridad
                                                         #, 'commitment_date' : self.x_studio_rango_inicial_de_visita
                                                         #, 'x_studio_fecha_final' : self.x_studio_rango_final_de_visita
                                                         , 'user_id' : self.user_id.id
                                                         , 'x_studio_tcnico' : self.x_studio_tcnico.id
                                                         , 'warehouse_id' : 5865   ##Id GENESIS AGRICOLA REFACCIONES  stock.warehouse
                                                         , 'team_id' : 1})
            #self.env.cr.commit()
            #for c in self.x_studio_field_tLWzF:
            for c in self.x_studio_productos:
                self.sudo().env['sale.order.line'].create({'order_id' : sale.id
                                                           , 'product_id' : c.id
                                                           , 'product_uom_qty' : c.x_studio_cantidad_pedida
                                                           ,'x_studio_field_9nQhR':self.x_studio_equipo_por_nmero_de_serie[0].id
                                                          })
                self['x_studio_field_nO7Xg'] = sale.id
                sale.sudo().env['sale.order'].write({'x_studio_tipo_de_solicitud' : 'Venta'})
                #self.env.invalidate_all()
                self.sudo().env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
                #self.env.cr.commit()
                
                if sale.id:
                    if self.x_studio_id_ticket:
                        #raise exceptions.ValidationError("error gerardo")
                        if self.stage_id.name == 'Atención' and self.team_id.name == 'Equipo de hardware':
                            query = "update helpdesk_ticket set stage_id = 100 where id = " + str(self.x_studio_id_ticket) + ";"
                            _logger.info("lol: " + query)
                            ss = self.env.cr.execute(query)
                            self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado':
                                                                     self.stage_id.name})
                
                
                
                
    #@api.onchange('x_studio_verificacin_de_refaccin')
    def validar_solicitud_refaccion(self):
        for record in self:
            sale = record.x_studio_field_nO7Xg
            self.sudo().env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
            sale.write({'x_studio_tipo_de_solicitud' : 'Venta'})
            sale.action_confirm()
    
    
    
    
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
            
    
    
    
    @api.onchange('x_studio_tipo_de_requerimiento')
    def toner(self):
      for record in self:  
        if (record.team_id.id == 8 ) and record.x_studio_tipo_de_requerimiento == 'Tóner':
            sale = self.env['sale.order'].create({'partner_id' : record.partner_id.id
                                            , 'origin' : "Ticket de tóner: " + str(record.x_studio_id_ticket)
                                            , 'x_studio_tipo_de_solicitud' : "Venta"
                                            , 'x_studio_requiere_instalacin' : True                                       
                                            , 'user_id' : record.user_id.id                                           
                                            , 'x_studio_tcnico' : record.x_studio_tcnico.id
                                            , 'warehouse_id' : 1   ##Id GENESIS AGRICOLA REFACCIONES  stock.warehouse
                                            , 'team_id' : 1      
                                          })
            record['x_studio_field_nO7Xg'] = sale.id
            for c in record.x_studio_seriestoner:
              _logger.info('*************cantidad a solicitar: ' + str(c.product_id.id))
              self.env['sale.order.line'].create({'order_id' : sale.id
                                            , 'product_id' : c.x_studio_toner_compatible.id
                                            , 'product_uom_qty' : 1.0
                                            ,'x_studio_field_9nQhR':c.id      
                                          })
            sale.env['sale.order'].write({'x_studio_tipo_de_solicitud' : 'Venta'})
            self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
        if (record.team_id.id == 13 ) and record.x_studio_tipo_de_requerimiento == 'Tóner':
            sale = self.env['sale.order'].create({'partner_id' : record.partner_id.id
                                            , 'origin' : "Ticket de tfs: " + str(record.x_studio_id_ticket)
                                            , 'x_studio_tipo_de_solicitud' : "Venta"
                                            , 'x_studio_requiere_instalacin' : True                                       
                                            , 'user_id' : record.user_id.id                                           
                                            , 'x_studio_tcnico' : record.x_studio_tcnico.id
                                            , 'warehouse_id' : 1   ##Id GENESIS AGRICOLA REFACCIONES  stock.warehouse
                                            , 'team_id' : 1      
                                          })
            record['x_studio_field_nO7Xg'] = sale.id
            for c in record.x_studio_seriestoner:
              #_logger.info('*************cantidad a solicitar: ' + str(c.x_studio_cantidad_a_solicitar))
              self.env['sale.order.line'].create({'order_id' : sale.id
                                            , 'product_id' : c.id
                                            , 'product_uom_qty' : 1.0
                                          })
            sale.env['sale.order'].write({'x_studio_tipo_de_solicitud' : 'Venta'})
            self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")    
            

    #@api.onchange('x_studio_verificacin_de_tner')
    def validar_solicitud_toner(self):
        _logger.info("validar_solicitud_toner()")        
        for record in self:
            sale = record.x_studio_field_nO7Xg
            self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
            sale.write({'x_studio_tipo_de_solicitud' : 'Venta'})
            sale.action_confirm()
            query="update helpdesk_ticket set stage_id = 92 where id = " + str(self.x_studio_id_ticket) + ";" 
            ss=self.env.cr.execute(query)
    
    @api.onchange('x_studio_desactivar_zona')
    def desactivar_datos_zona(self):
        res = {}
        if self.x_studio_desactivar_zona :
           res['domain']={'x_studio_responsable_de_equipo':[('x_studio_zona', '!=', False)]}
        return res
       
    #@api.model            
    @api.onchange('x_studio_activar_compatibilidad')
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
           
    @api.onchange('x_studio_tcnico')
    def actualiza_datos_zona(self):
        s = self.x_studio_tcnico.name
        b = self.stage_id.name
        self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': s,'x_estado': b })
    
    
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
                 record['x_studio_seriestoner'] = ''
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
               action = {'domain':{'x_studio_seriestoner':dominio}}
            if self.team_id.id!=8:
               action = {'domain':{'x_studio_equipo_por_nmero_de_serie':dominio}}    
            return action
    
    
    #@api.model
    #@api.multi
    @api.onchange('x_studio_equipo_por_nmero_de_serie','x_studio_seriestoner')
    #@api.depends('x_studio_equipo_por_nmero_de_serie')
    def actualiza_datos_cliente(self):
        _logger.info("actualiza_datos_cliente()")
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


                _logger.info('*********x_studio_seriestoner: ')
                _logger.info(str(record.x_studio_seriestoner))
                for numeros_serie in record.x_studio_seriestoner:
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
                    v['x_studio_seriestoner'] = lista_ids
                    self._origin.sudo().write({'x_studio_seriestoner' : lista_ids})
                    record.x_studio_seriestoner = lista_ids
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
    contadorAnteriorMono=fields.Integer(related='contadorAnterior.contadorMono',string='Anterior Monocromatico')
    contadorAnteriorColor=fields.Integer(related='contadorAnterior.contadorColor',string='Anterior Color')
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
