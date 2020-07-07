from odoo import fields, api
from odoo.models import TransientModel
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from odoo import exceptions, _


class dca_editar_contadores(TransientModel):
    _name = 'contadores.dca.editar.contadores'
    _description = 'helpdesk permite editar los contadores actuales.'

    dca_id = fields.Many2one("dcas.dcas")

    
    serieSeleccionada = fields.Text(
                            string = 'Serie seleccionada',
                            compute = "_compute_serieSeleccionada"
                        )
    dominio = fields.Text(
                            string = 'Dominio',
                            store = True
                        )
    tipoEquipo = fields.Selection(
                                    [('Color','Color'),('B/N','B/N')],
                                    string = 'Equipo color o B/N',
                                    compute = '_compute_equipoSeleccionado'
                                )
    contadorMonoActual = fields.Integer(
                                            string = 'Contador Monocromatico actual',
                                            store = False,
                                            compute = '_compute_contador_bn_actual'
                                        )
    contadorColorActual = fields.Integer(
                                            string = 'Contador Color actual',
                                            store = False,
                                            compute = '_compute_contador_color_actual'
                                        )
    contadorMonoActualizado = fields.Integer(
                                                string = 'Contador Monocromatico nuevo',
                                                store = True
                                            )
    contadorColorActualizado = fields.Integer(
                                                string = 'Contador Color nuevo',
                                                store = True
                                            )

    evidencia = fields.Many2many(
                                    'ir.attachment',
                                    string = "Evidencias"
                                )
    comentario = fields.Text(
                                string = 'Comentario'
                            )
    check = fields.Boolean(
                                string = 'Mostrar en reporte',
                                default = False
                            )
    estado = fields.Char(
                            string = 'Estado', 
                            compute = "_compute_estadoTicket"
                        )

    def _compute_equipoSeleccionado(self):
        if self.dca_id.colorEquipo:
            self.tipoEquipo = self.dca_id.colorEquipo

    def _compute_serieSeleccionada(self):
        if self.dca_id.serie:
            self.serieSeleccionada = self.dca_id.serie.name

    def _compute_estadoTicket(self):
        if self.dca_id.x_studio_tiquete:
            self.estado = self.dca_id.x_studio_tiquete.stage_id.name

    def _compute_contador_bn_actual(self):
        if self.dca_id.contadorMono:
            self.contadorMonoActual = self.dca_id.contadorMono

    def _compute_contador_color_actual(self):
        if self.dca_id.contadorColor:
            self.contadorColorActual = self.dca_id.contadorColor

    def actualizaContador(self):
        if self.tipoEquipo == 'B/N':
            if self.contadorMonoActualizado >= self.contadorMonoActual:
                self.dca_id.contadorMono = self.contadorMonoActualizado
                #todo bien
                self.dca_id.vcalcula()
                self.env['helpdesk.diagnostico'].create({
                                                            'ticketRelacion': self.dca_id.x_studio_tiquete.id,
                                                            'comentario': self.comentario,
                                                            'estadoTicket': self.dca_id.x_studio_tiquete.stage_id.name,
                                                            'evidencia': [(6,0,self.evidencia.ids)],
                                                            'mostrarComentario': self.check
                                                        })
                mensajeTitulo = 'Actualización de contador exitosa'
                mensajeCuerpo = 'Se logro actualizar el contador mono'
                wiz = self.env['contadores.dca.alerta'].create({'dca_id': self.dca_id.id, 'mensaje': mensajeCuerpo})
                view = self.env.ref('contadores.view_dca_alerta')
                return {
                            'name': _(mensajeTitulo),
                            'type': 'ir.actions.act_window',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_model': 'contadores.dca.alerta',
                            'views': [(view.id, 'form')],
                            'view_id': view.id,
                            'target': 'new',
                            'res_id': wiz.id,
                            'context': self.env.context,
                        }
            else:
                #no se puede actualizar por contador mono es menor
                mensajeTitulo = 'Actualización de contador no completada'
                mensajeCuerpo = 'No se logro actualizar el contador debido a que el contador mono actual es menor que el contador mono a capturar'
                wiz = self.env['contadores.dca.alerta'].create({'dca_id': self.dca_id.id, 'mensaje': mensajeCuerpo})
                view = self.env.ref('contadores.view_dca_alerta')
                return {
                            'name': _(mensajeTitulo),
                            'type': 'ir.actions.act_window',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_model': 'contadores.dca.alerta',
                            'views': [(view.id, 'form')],
                            'view_id': view.id,
                            'target': 'new',
                            'res_id': wiz.id,
                            'context': self.env.context,
                        }
        elif self.tipoEquipo == 'Color':
            if self.contadorColorActualizado >= self.contadorColorActual:
                if contadorMonoActualizado >= self.contadorMonoActual:
                    self.dca_id.contadorMono = self.contadorMonoActualizado
                else:
                    #no se puede actualizar por contador mono es menor
                    mensajeTitulo = 'Actualización de contador no completada'
                    mensajeCuerpo = 'No se logro actualizar el contador debido a que el contador mono actual es menor que el contador mono a capturar'
                    wiz = self.env['contadores.dca.alerta'].create({'dca_id': self.dca_id.id, 'mensaje': mensajeCuerpo})
                    view = self.env.ref('contadores.view_dca_alerta')
                    return {
                                'name': _(mensajeTitulo),
                                'type': 'ir.actions.act_window',
                                'view_type': 'form',
                                'view_mode': 'form',
                                'res_model': 'contadores.dca.alerta',
                                'views': [(view.id, 'form')],
                                'view_id': view.id,
                                'target': 'new',
                                'res_id': wiz.id,
                                'context': self.env.context,
                            }
                self.dca_id.contadorColor = self.contadorColorActualizado
                #todo bien
                self.dca_id.vcalcula()
                self.env['helpdesk.diagnostico'].create({
                                                            'ticketRelacion': self.dca_id.x_studio_tiquete.id,
                                                            'comentario': self.comentario,
                                                            'estadoTicket': self.dca_id.x_studio_tiquete.stage_id.name,
                                                            'evidencia': [(6,0,self.evidencia.ids)],
                                                            'mostrarComentario': self.check
                                                        })
                mensajeTitulo = 'Actualización de contador exitosa'
                mensajeCuerpo = 'Se logro actualizar el contador color y mono'
                wiz = self.env['contadores.dca.alerta'].create({'dca_id': self.dca_id.id, 'mensaje': mensajeCuerpo})
                view = self.env.ref('contadores.view_dca_alerta')
                return {
                            'name': _(mensajeTitulo),
                            'type': 'ir.actions.act_window',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_model': 'contadores.dca.alerta',
                            'views': [(view.id, 'form')],
                            'view_id': view.id,
                            'target': 'new',
                            'res_id': wiz.id,
                            'context': self.env.context,
                        }
            else:
                #no se puede actualizar porque el contador color es menor
                mensajeTitulo = 'Actualización de contador no completada'
                mensajeCuerpo = 'No se logro actualizar el contador debido a que el contador color actual es menor que el contador color a capturar'
                wiz = self.env['contadores.dca.alerta'].create({'dca_id': self.dca_id.id, 'mensaje': mensajeCuerpo})
                view = self.env.ref('contadores.view_dca_alerta')
                return {
                            'name': _(mensajeTitulo),
                            'type': 'ir.actions.act_window',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_model': 'contadores.dca.alerta',
                            'views': [(view.id, 'form')],
                            'view_id': view.id,
                            'target': 'new',
                            'res_id': wiz.id,
                            'context': self.env.context,
                        }

class DcaAlerta(TransientModel):
    _name = 'contadores.dca.alerta'
    _description = 'Dca Alerta'
    
    dca_id = fields.Many2one("dcas.dcas")
    mensaje = fields.Text('Mensaje')



class dca_reiniciar_contadores(TransientModel):
    _name = 'contadores.dca.reiniciar.contadores'
    _description = 'helpdesk permite reiniciar los contadores actuales.'

    dca_id = fields.Many2one("dcas.dcas")

    serieSeleccionada = fields.Text(
                            string = 'Serie seleccionada',
                            compute = "_compute_serieSeleccionada"
                        )
    dominio = fields.Text(
                            string = 'Dominio',
                            store = True
                        )
    tipoEquipo = fields.Selection(
                                    [('Color','Color'),('B/N','B/N')],
                                    string = 'Equipo color o B/N',
                                    compute = '_compute_equipoSeleccionado'
                                )
    contadorMonoActual = fields.Integer(
                                            string = 'Contador Monocromatico actual',
                                            store = False,
                                            compute = '_compute_contador_bn_actual'
                                        )
    contadorColorActual = fields.Integer(
                                            string = 'Contador Color actual',
                                            store = False,
                                            compute = '_compute_contador_color_actual'
                                        )
    contadorMonoActualizado = fields.Integer(
                                                string = 'Contador Monocromatico nuevo',
                                                store = True,
                                                default = 0
                                            )
    contadorColorActualizado = fields.Integer(
                                                string = 'Contador Color nuevo',
                                                store = True,
                                                default = 0
                                            )

    evidencia = fields.Many2many(
                                    'ir.attachment',
                                    string = "Evidencias"
                                )
    comentario = fields.Text(
                                string = 'Comentario'
                            )
    check = fields.Boolean(
                                string = 'Mostrar en reporte',
                                default = False
                            )
    estado = fields.Char(
                            string = 'Estado', 
                            compute = "_compute_estadoTicket"
                        )

    def _compute_equipoSeleccionado(self):
        if self.dca_id.colorEquipo:
            self.tipoEquipo = self.dca_id.colorEquipo

    def _compute_serieSeleccionada(self):
        if self.dca_id.serie:
            self.serieSeleccionada = self.dca_id.serie.name

    def _compute_estadoTicket(self):
        if self.dca_id.x_studio_tiquete:
            self.estado = self.dca_id.x_studio_tiquete.stage_id.name

    def _compute_contador_bn_actual(self):
        if self.dca_id.contadorMono:
            self.contadorMonoActual = self.dca_id.contadorMono

    def _compute_contador_color_actual(self):
        if self.dca_id.contadorColor:
            self.contadorColorActual = self.dca_id.contadorColor

    def reiniciarContadores(self):
        dcaGenerado = self.env['dcas.dcas'].create({
                                        'tablahtml': self.dca_id.tablahtml,
                                        'x_studio_cliente': self.dca_id.x_studio_cliente,
                                        'serie': self.dca_id.serie.id,
                                        'x_studio_color_o_bn': self.dca_id.x_studio_color_o_bn,
                                        'x_studio_cartuchonefro': self.dca_id.x_studio_cartuchonefro.id,
                                        'x_studio_rendimiento_negro': self.dca_id.x_studio_rendimiento_negro,
                                        'x_studio_cartucho_amarillo': self.dca_id.x_studio_cartucho_amarillo.id,
                                        'x_studio_rendimientoa': self.dca_id.x_studio_rendimientoa,
                                        'x_studio_cartucho_cian_1': self.dca_id.x_studio_cartucho_cian_1.id,
                                        'x_studio_rendimientoc': self.dca_id.x_studio_rendimientoc,
                                        'x_studio_cartucho_magenta': self.dca_id.x_studio_cartucho_magenta.id,
                                        'x_studio_rendimientom': self.dca_id.x_studio_rendimientom,
                                        'x_studio_fecha': self.dca_id.x_studio_fecha,
                                        'x_studio_tiquete': self.dca_id.x_studio_tiquete.id,
                                        'x_studio_tickett': self.dca_id.x_studio_tickett,
                                        'fuente': self.dca_id.fuente,

                                        'contadorColor': self.contadorColorActualizado,
                                        'x_studio_contador_color_anterior': self.dca_id.x_studio_contador_color_anterior,
                                        'contadorMono': self.contadorMonoActualizado,
                                        'x_studio_contador_mono_anterior_1': self.dca_id.x_studio_contador_mono_anterior_1,

                                        'paginasProcesadasBN': self.dca_id.paginasProcesadasBN,
                                        'porcentajeNegro': self.dca_id.porcentajeNegro,
                                        'porcentajeAmarillo': self.dca_id.porcentajeAmarillo,
                                        'porcentajeCian': self.dca_id.porcentajeCian,
                                        'porcentajeMagenta': self.dca_id.porcentajeMagenta,
                                        'x_studio_rendimiento': self.dca_id.x_studio_rendimiento,
                                        'x_studio_rendimiento_color': self.dca_id.x_studio_rendimiento_color,
                                        'x_studio_toner_negro': self.dca_id.x_studio_toner_negro,
                                        'x_studio_toner_cian': self.dca_id.x_studio_toner_cian,
                                        'x_studio_toner_magenta': self.dca_id.x_studio_toner_magenta,
                                        'x_studio_toner_amarillo': self.dca_id.x_studio_toner_amarillo,
                                        'nivelCA': self.dca_id.nivelCA,
                                        'nivelMA': self.dca_id.nivelMA,
                                        'nivelNA': self.dca_id.nivelNA,
                                        'nivelAA': self.dca_id.nivelAA,
                                        'contadorAnteriorNegro': self.dca_id.contadorAnteriorNegro,
                                        'contadorAnteriorAmarillo': self.dca_id.contadorAnteriorAmarillo,
                                        'contadorAnteriorMagenta': self.dca_id.contadorAnteriorMagenta,
                                        'contadorAnteriorCian': self.dca_id.contadorAnteriorCian,
                                        'paginasProcesadasA': self.dca_id.paginasProcesadasA,
                                        'paginasProcesadasC': self.dca_id.paginasProcesadasC,
                                        'paginasProcesadasM': self.dca_id.paginasProcesadasM,
                                        'renM': self.dca_id.renM,
                                        'renA': self.dca_id.renA,
                                        'renC': self.dca_id.renC
                                    })
        self.dca_id.x_studio_tiquete.x_studio_equipo_por_nmero_de_serie_1 = [(6, 0, dcaGenerado.ids)]
        dcaGenerado.vcalcula()
        self.env['helpdesk.diagnostico'].create({
                                                    'ticketRelacion': self.dca_id.x_studio_tiquete.id,
                                                    'comentario': self.comentario,
                                                    'estadoTicket': self.dca_id.x_studio_tiquete.stage_id.name,
                                                    'evidencia': [(6,0,self.evidencia.ids)],
                                                    'mostrarComentario': self.check
                                                })
        mensajeTitulo = 'Reinicio de contadores exitoso'
        mensajeCuerpo = 'Se reiniciaron los contadores de la serie seleccionada.'
        wiz = self.env['contadores.dca.alerta'].create({'dca_id': self.dca_id.id, 'mensaje': mensajeCuerpo})
        view = self.env.ref('contadores.view_dca_alerta')
        return {
                    'name': _(mensajeTitulo),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'contadores.dca.alerta',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': self.env.context,
                }