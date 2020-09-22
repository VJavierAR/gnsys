from odoo import fields, api
from odoo.models import TransientModel
import logging, ast
import datetime, time
import pytz
import base64
import xlsxwriter

_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from odoo import exceptions, _


class GastoPagoReporte(TransientModel):
    _name = 'gasto.pago.reporte'
    _description = 'Reporte de gastos'
    fechaInicial = fields.Date(string = 'Fecha inicial',store = True)
    fechaFinal = fields.Date(string = 'Fecha final',store = True)
    otro = fields.Boolean()
    excelD = fields.Binary(string="Documento Excel")
    
    
    
    def report(self):
        
        
        i=[]
        d=[]
        
        
        
        fechaHoy = str(datetime.date.today())
        fechaHoy = fechaHoy.split('-')
        
        fecha2 = datetime.datetime(int(fechaHoy[0]), int(fechaHoy[1]), int(fechaHoy[2]))
                               
        if self.fechaInicial :
            fechaCompleta = str(self.fechaInicial).split(' ')[0]
            fechaCompleta = fechaCompleta.split('-')
            fecha1 = datetime.datetime(int(fechaCompleta[0]), int(fechaCompleta[1]), int(fechaCompleta[2]))
            
            
            m=['fecha','>=',self.fechaInicial]
            i.append(m)
            
            
            if fecha1 > fecha2 :
                # self.fechaLimite = datetime.datetime.now()
                raise exceptions.ValidationError("La fecha inicial de reporte no puede ser mayor al día de hoy .")
                
                
        if self.fechaFinal :
            fechaCompleta = str(self.fechaFinal).split(' ')[0]
            fechaCompleta = fechaCompleta.split('-')
            fecha1 = datetime.datetime(int(fechaCompleta[0]), int(fechaCompleta[1]), int(fechaCompleta[2]))
            
            
            m=['fecha','<=',self.fechaFinal]
            i.append(m)
            
            
            if fecha1 > fecha2 :
                # self.fechaLimite = datetime.datetime.now()
                raise exceptions.ValidationError("La fecha final de reporte no puede ser mayor al día de hoy .")
      
        
        
        d=self.env['gastos.devolucion'].search(i,order='fecha asc')
        _logger.info(str(len(d)))
        _logger.info("||||-:   "+str(len(d)))
        
        
        
        return self.env.ref('gastos_gnsys.pagos_xlsx').report_action(d)
        
    

    
    
    
    
    
        
        
    

    