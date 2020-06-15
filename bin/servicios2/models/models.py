# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo import exceptions

class SaleSubscription(models.Model):
    _inherit = ['sale.subscription']
    campo_prueba = fields.Char(string="Campo_prueba")
    otro_campo = fields.Char(string="Otro campo")
    #series_lines_info = fields.one2Many
    
    
    def recurring_invoice(self):
       # mensaje = 'mi mensaje'
        for record in self:
            record['campo_prueba'] = 'mi funcion hizo esto'
        return 

    def recurring_invoice2(self):
        #mensaje = 'mi mensaje'
        self._recurring_create_invoice()
        return self.action_subscription_invoice()
    #Genera la factura de la suscripcion (se inabilitó la facturacions recurrente 
    #ahora se hace por este medio en el boton generar factura
    @api.multi
    def validar_suscripcion(self):
        self.campo_prueba = 'Suscripcion valida'
        self._recurring_create_invoice()
        return self.action_subscription_invoice()
        #return {
         #   'type': 'ir.action.act_url',
          #  'url' : '/web#id=%s&action=625&model=account.invoice&view_type=form&menu_id=406' % (1632),
           # 'target' :'new'
  #          'res_id': self.id}

        #Recolecta las lecturas de los equpos instalados en la suscripción

   # @api.model
    def collect_lecturas(self):
        #objecto que contendra los numeros de serie de todos los equipos de la suscripcion
        no_de_serie = list()
        equipos = list()
         #obteniendo los equipos por su numero de serie
        for record in self:
            series = record.x_studio_field_hmETe
            i = 0
            if(len(series) >= 0):
                for serie in series:
               
                   # trajendo la informacion de los numeros de serie
                    no_de_serie.append(self.env['stock.production.lot'].sudo().search_read([('id','=',serie.lot_id.id)]))
                    
            #obteniendo las lecturas de cada equipo
        dcas = list()
        
        for equipo in no_de_serie[0]:
            dcas.append({'equipo':equipo['name'],'dcas':equipo['x_studio_field_B7uLt']})
            line_cont_sus = {
                'num_serie': equipo.name,
                'consumo_bn': equipo.x_studio_contador_bn - equipo.x_studio_contador_anterior,
                'consumo_color': equipo.x_studio_contador_color - equipo.x_studio_contador_color_anterior
                #'ultimo_corte' : equipo.
            }
        self.campo_prueba = 'funcion chida' + str( dcas) # equipos[0]['name']
        #self.env['cont_suscripcion'].calcular_consumos(1,2).sudo()
        
        #creando cont_suscriptions lines
        
        return
    #busca las 2 ultimas lecturas validas de dos dcas 
    #@param lecturas: dict- dictionary 2 ultimas lecturas cont_bn y cont_color
    def buscar_ultimas_lecturas(serie):
        print("algo")
        
            
            
        #return 
#Modelo para guardar mostrar y almacenar los que se va a cobrar
class cont_suscripcion(models.Model):
    _name = 'contadores_suscripcion'
    _description = "Contadores de la suscripción"

    name = fields.Char()
    consumo_bn = fields.Float(string = "Consumo b/n")
    consumo_color  =fields.Float(string = "Consumo color")
    num_serie = fields.Char(string = 'No serie')
    ultimo_corte = fields.Date(string = 'Fecha del último corte')
    suscription_reference = fields.Many2one("sale.subscription",ondelete = "set null", string= 'Referencia suscripción')
    equipo_instalado = fields.Boolean("Equipo instalado")
    id_ultimo_dca = fields.Integer()
    id_localidad = fields.Many2one('res.partner',ondelete = 'set null', string = 'Localidad')
    modelo = fields.Char(related='')
    
    def calcular_consumos(self):
        return {
            'warning': {
                'title': 'Warning!',
                'message': 'dca1: ' + str(dca1) + ' dca2: ' + str(dca2)
            }
        }
  
    def obtener_ultimo_corte(self):

        equipo = self.env['stock.production.lot'].sudo().search_read([('name','=',self.num_serie)],['name','x_studio_ultima_ubicacin','x_studio_field_B7uLt'])
        #validando que el equipo este en la localidad
        #raise exceptions.Warning(equipo)
        for record in self:
            if(equipo != '' and len(equipo) > 0):
                print("algo")
                en_localidad = False

                localidades  = record.suscription_reference.x_studio_field_13R0x

                #raise exceptions.Warning(equipo[0]['x_studio_ultima_ubicacin'])
                for localidad in localidades:
                    #raise exceptions.Warning(str(equipo[0]['x_studio_ultima_ubicacin']))
                    nombre_loc = localidad.parent_id.name + ", " + localidad.name
                  #  raise exceptions.Warning(str(equipo[0]['x_studio_ultima_ubicacin'] ) + " " + str(nombre_loc))
                    #verficasndo que el equipo este en la localidad
                    if(nombre_loc == equipo[0]['x_studio_ultima_ubicacin']):
                        en_localidad = True
                        #Recogiendo los contadores del equipo


                        #raise exceptions.Warning("el numero de serie esta en la localidad")
                    else:
                        raise exceptions.Warning("El equipo no se encuentra en alguna localidad de la suscripcion")
                    if (en_localidad):
                        id_localidad = equipo[0].x_studio_ultima_ubicacin
                        raise exceptions.Warning(id_localidad.name)
               # en_localidad = localidades.filtered(lambda localidad: localidad.parent_id.name + ", " + localidad.name == equipo[0]['x_studio_ultima_ubicacin'] + 'df')
                #raise exceptions.Warning(str(en_localidad))
               # if(equipo['ubicacion'] > )
            else:
               # raise exceptions.Warning( 'No existe un equipo con el numero de serie ' + str(self.num_serie))
                return {
                    'warning': {
                        'title': 'Warning!',
                        'message': 'No existe un equipo con el numero de serie ' + str(self.num_serie)
                        }
                    }
        #Este es un comentario que voy a poner desde git
        #otro coment
        #raise UserError(_(str(equipo)))
        
       
        
    #     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100