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
        bold = workbook.add_format({'bold': True, 'bg_color': '#DBD9D9'})
        
        
        
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
        
        quienesReciben = "-"
        fecha = "-"
        formaDePago = "-"
        banco = "-"
        banco1 = ['bajio','BAJIO','banamex','BANAMEX','banorte','BANORTE','santnder','SANTANDER','hsbc','HSBC','azteca','AZTECA','bancomer','BANCOMER']
        claveInterbancaria = "-"
        montodeNoDucibleI = 0.0
        fechaTransf = "-"
        montodeDucibleI = 0.0
        fechaTransfDeducible = "-"
        fechaLimite = "-"
        montoEntregado = 0.0
        
        contador = 0
        for objeto in partners:
            banco = "-"
            contador = 0
            for o in banco1: 
                if o == objeto.banco :
                    banco = banco1[contador+1]
                contador += 1
            
            _logger.info("||||-:   {"+str(banco))

            quienesReciben = "-"
            fecha = "-"
            formaDePago = "-"
            
            claveInterbancaria = "-"
            montodeNoDucibleI = 0.0
            fechaTransf = "-"
            montodeDucibleI = 0.0
            fechaTransfDeducible = "-"
            fechaLimite = "-"
            montoEntregado = 0.0
            if (objeto.quienesReciben.name != False) : 
                quienesReciben = str(objeto.quienesReciben.name)
            if (objeto.fecha != False) : 
                fecha = str(objeto.fecha)  
            if (objeto.formaDePago != False) : 
                formaDePago = str(objeto.formaDePago)
            if (objeto.banco != False) : 
                banco = banco
            if (objeto.claveInterbancaria != False) : 
                claveInterbancaria = str(objeto.claveInterbancaria)
            if (objeto.montodeNoDucibleI != False) : 
                montodeNoDucibleI = objeto.montodeNoDucibleI
            if (objeto.fechaTransf != False) : 
                fechaTransf = str(objeto.fechaTransf)
            if (objeto.montodeDucibleI != False) : 
                montodeDucibleI = objeto.montodeDucibleI
            if (objeto.fechaTransfDeducible != False) : 
                fechaTransfDeducible = str(objeto.fechaTransfDeducible)
            if (objeto.fechaLimite != False) : 
                fechaLimite = str(objeto.fechaLimite)
            if (objeto.montoEntregado != False) : 
                montoEntregado = objeto.montoEntregado

            
            # _logger.info("||||-:   -"+str( objeto.quienesReciben.name))
            # _logger.info("||||-:   -"+str( objeto.fecha))
            # _logger.info("||||-:   -"+str( objeto.formaDePago))
            # _logger.info("||||-:   -"+str( objeto.banco))
            # _logger.info("||||-:   -"+str( objeto.claveInterbancaria))



            # _logger.info("||||-:   -"+str( objeto.montodeNoDucibleI))
            # _logger.info("||||-:   -"+str( objeto.fechaTransf))
            # _logger.info("||||-:   -"+str( objeto.montodeDucibleI))


            # _logger.info("||||-:   -"+str( objeto.fechaTransfDeducible))
            # _logger.info("||||-:   -"+str( objeto.fechaLimite))
            # _logger.info("||||-:   -"+str( objeto.montoEntregado))            
            sheet.write(row_number, col_number , quienesReciben)
            sheet.write(row_number, col_number + 1, fecha)
            sheet.write(row_number, col_number + 2, formaDePago)
            sheet.write(row_number, col_number + 3, banco)
            sheet.write(row_number, col_number + 4, claveInterbancaria)
            sheet.write(row_number, col_number + 5, montodeNoDucibleI)
            sheet.write(row_number, col_number + 6, fechaTransf)
            sheet.write(row_number, col_number + 7, montodeDucibleI)
            sheet.write(row_number, col_number + 8, fechaTransfDeducible)
            sheet.write(row_number, col_number + 9, fechaLimite)
            sheet.write(row_number, col_number + 10, montoEntregado)
            
            row_number += 1
            #_logger.info("||||-:   "+str(obj.fecha))
        

        sheet.write(row_number, 4 , 'Total a depositar no deducible' , bold)
        sheet.write(row_number, 5 , '=SUM(F2:F' + str(row_number) + ')' )



        sheet.write(row_number, 6 , 'Depositos deducibles' , bold)
        sheet.write(row_number, 7 , '=SUM(G2:G' + str(row_number) + ')' )




        sheet.write(row_number, 9 , 'Depositos deducibles' , bold)
        sheet.write(row_number, 10 , '=SUM(K2:K' + str(row_number) + ')' )
        