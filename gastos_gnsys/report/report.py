from odoo import models
import logging, ast
import datetime, time
import xlsxwriter
import pytz
_logger = logging.getLogger(__name__)

class PartnerXlsx(models.AbstractModel):
    
    _name = 'report.gastos_gnsys.report_pagos_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        # Se declara hoja del excel
        sheet = workbook.add_worksheet('Reporte de pagos')
        bold = workbook.add_format({'bold': True})
        
        
        
        cabecera = ['Quien recibe' ,'Fecha','Forma de pago','Banco','Clave interbancaria','Monto no dedicible','Fecha de transferencia','Monto dedicible','Fecha de transferencia deducible','Fecha Limite','Monto entregado']
        #Pintar la cabecera del excel
        row_number = 0
        col_number = 0
        for objeto in cabecera:
            
            sheet.write(row_number, col_number, objeto, bold)
            col_number += 1
        #Pintar los datos del reporte de acuerdo a la fecha
        row_number = 1
        col_number = 0
        
            
        for objeto in partners:
            if (objeto.quienesReciben.name == False) : 
                objeto.quienesReciben.name = ""
            if (objeto.fecha == False) : 
                objeto.fecha = ""
            if (objeto.formaDePago == False) : 
                objeto.formaDePago = ""
            if (objeto.banco == False) : 
                objeto.banco = ""
            if (objeto.claveInterbancaria == False) : 
                objeto.claveInterbancaria = ""
            if (objeto.montodeNoDucibleI == False) : 
                objeto.montodeNoDucibleI = ""
            if (objeto.fechaTransf == False) : 
                objeto.fechaTransf = ""
            if (objeto.montodeDucibleI == False) : 
                objeto.montodeDucibleI = ""
            if (objeto.fechaTransfDeducible == False) : 
                objeto.fechaTransfDeducible = ""
            if (objeto.fechaLimite == False) : 
                objeto.fechaLimite = ""

            if (objeto.montoEntregado == False) : 
                objeto.montoEntregado = ""

            
            _logger.info("||||-:   -"+str( objeto.quienesReciben.name))
            _logger.info("||||-:   -"+str( objeto.fecha))
            _logger.info("||||-:   -"+str( objeto.formaDePago))
            _logger.info("||||-:   -"+str( objeto.banco))
            _logger.info("||||-:   -"+str( objeto.claveInterbancaria))



            _logger.info("||||-:   -"+str( objeto.montodeNoDucibleI))
            _logger.info("||||-:   -"+str( objeto.fechaTransf))
            _logger.info("||||-:   -"+str( objeto.montodeDucibleI))


            _logger.info("||||-:   -"+str( objeto.fechaTransfDeducible))
            _logger.info("||||-:   -"+str( objeto.fechaLimite))
            _logger.info("||||-:   -"+str( objeto.montoEntregado))            
            # sheet.write(row_number, col_number , objeto.quienesReciben.name)
            # sheet.write(row_number, col_number + 1, objeto.fecha)
            # sheet.write(row_number, col_number + 2, objeto.formaDePago)
            # sheet.write(row_number, col_number + 3, objeto.banco)
            # sheet.write(row_number, col_number + 4, objeto.claveInterbancaria)
            # sheet.write(row_number, col_number + 5, objeto.montodeNoDucibleI)
            # sheet.write(row_number, col_number + 6, objeto.fechaTransf)
            # sheet.write(row_number, col_number + 7, objeto.montodeDucibleI)
            # sheet.write(row_number, col_number + 8, objeto.fechaTransfDeducible)
            # sheet.write(row_number, col_number + 9, objeto.evidencia)
            # sheet.write(row_number, col_number + 10, objeto.fechaLimite)
            # sheet.write(row_number, col_number + 11, objeto.montoEntregado)
            
            row_number += 1
            #_logger.info("||||-:   "+str(obj.fecha))