from odoo import fields, api
from odoo.models import TransientModel
import logging, ast
import datetime, time
import pytz
import io,csv
import datetime
import xlsxwriter 
import base64

import xmlrpc.client
from datetime import date
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from odoo import exceptions, _



def get_cleinte():
    #info = xmlrpc.client.ServerProxy('https://gnsys-corp-sta-1642577.dev.odoo.com/start').start()
    #url, db, username, password = \
    #info['https://gnsys-corp-sta-1642577.dev.odoo.com'], info['gnsys-corp-sta-1642577'], info['equipo.odoo@scgenesis.mx'], info['krizaldi1989']
    #common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format("https://gnsys-corp-sta-1642577.dev.odoo.com"))
    #common.version()
    #uid = common.authenticate('gnsys-corp-sta-1642577','Administrador', 'krizaldi1989', {})
    #models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format("https://gnsys-corp-sta-1642577.dev.odoo.com"))
    
    """
    url='https://gnsys-corp-sta-1642577.dev.odoo.com'
    password='krizaldi1989'
    username='equipo.odoo@scgenesis.mx'
    db='gnsys-corp-sta-1642577'
    common=xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid=common.authenticate(db,username,password,{})
    models=xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    """
    """
    clientes=models.execute_kw('gnsys-corp-sta-1642577', 2,'krizaldi1989',
    'res.partner', 'search',
    [[['is_company', '=', True]]])
    """
    
    year_list = []
    for i in range(2010, 2036):
       year_list.append((i, str(i)))
    return year_list



class TestReport(TransientModel):
    _name = 'account.reporte'
    _description = 'Excel de reporte'
    
    
    
    """
    def _default_invoice_ids(self):
        return self.env['account.invoice'].browse(
            self.env.context.get('active_ids')
        )

    invoice_ids = fields.Many2many(
        string = 'Invoices',
        comodel_name = "account.invoice",
        default = lambda self: self._default_invoice_ids(),
        help = "",
    )
    """

    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    anio= fields.Selection(get_cleinte(), string='Cliente')     

    
    
    
    def get_Rfc():
        dir=self.env['res.partner'].search([('company_type','=','company')],order='create_date desc',limit=10) 
        year_list = []
        for i in dir:
           year_list.append((i.vat, str(i.vat)))
        return year_list
    
    
    
    def alv(self):
        workbook = xlsxwriter.Workbook('Example23.xlsx')
        dir=self.serie=self.env['account.invoice'].search([('type','!=','in_invoice'),('type','!=','in_refund'),('date_invoice','!=',False),('state','!=','draft')],order='create_date desc') 
        
        worksheet = workbook.add_worksheet('Reporte Facturacion')
        content = ["Serie", "Folio","Folio Fiscal Factura", "Documento Origen", "Folio Techra","RFC CLiente", "RFC Empresa","Razon Social", "Cliente", "Fecha Factura", "Importe sin impuesto","IVA","Total","Total adeudado","Tipo","Periodo","NC´s","REP","Retencion","Folio Fiscal Pago","Banco","Cuenta ordenate","Cuenta beneficiaria","Estado del pago","Ejecutivo","Vendedor","referencia","Fecha de pago","Pagos","Fecha Captura","Fecha Comentario","observaciones","Usuariocxc","Estado"]
        bold = workbook.add_format({'bold': True})
        neg = workbook.add_format({'border': 2})
        format6 = workbook.add_format({'num_format': 'dd-mm-yy'})
        i=0
        for item in content :           
            worksheet.write(0, i, item,neg)            
            #row += 1
            i=i+1
        
        i=1
        for f in dir:
            worksheet.write(i, 0, str(f.x_studio_serie))
            worksheet.write(i, 1, f.x_studio_folio_1)
            if str(f.x_studio_folio)=='No tiene timbre':
               worksheet.write(i, 2, str(f.x_studio_uuidtechra))
            else:
               worksheet.write(i, 2, str(f.x_studio_folio))
            
            if f.origin:
               worksheet.write(i, 3, str(f.origin))
            else:
               worksheet.write(i, 3, '')
            if f.x_studio_folio_techra:
               worksheet.write(i, 4, str(f.x_studio_folio_techra))
            else:
                worksheet.write(i, 4, '')
            
            worksheet.write(i, 6, str(f.company_id.vat))
            
            if f.x_studio_importacion=='pruebaNota' or f.x_studio_importacion=='lunes-19-10-2020' or f.x_studio_importacion=='lunes05' or f.x_studio_importacion=='viernes-30-10-2020' or f.x_studio_importacion=='lunes' or f.x_studio_importacion=='prueba' or f.x_studio_importacion=='martesGRupo':
              worksheet.write(i, 7, f.x_studio_razn_social_del_emisor)
              worksheet.write(i, 5, f.x_studio_rfc)
            else:  
              rz=dict(f.partner_id._fields['razonSocial'].selection).get(f.partner_id.razonSocial)
              worksheet.write(i, 7, rz)
              worksheet.write(i, 5, str(f.partner_id.vat))
            
            
            
            
            if str(f.partner_id.name)=='sin contacto':
               worksheet.write(i, 8, f.x_studio_cliente)
            else:
               worksheet.write(i, 8, str(f.partner_id.name))
            
            worksheet.write(i, 9, f.date_invoice,format6)
            worksheet.write(i, 10, f.amount_untaxed)
            worksheet.write(i, 11, f.amount_tax)
            worksheet.write(i, 12, f.amount_total)
            if f.type=='out_refund' and f.x_studio_importacion=='pruebaNota':
               worksheet.write(i, 13, 0.0)
            if (f.x_studio_importacion=='pruebaNota' or f.x_studio_importacion=='lunes-19-10-2020' or f.x_studio_importacion=='lunes05' or f.x_studio_importacion=='viernes-30-10-2020' or f.x_studio_importacion=='lunes' or f.x_studio_importacion=='prueba' or f.x_studio_importacion=='martesGRupo') and f.state=='open':
               worksheet.write(i, 13, float(f.x_studio_importe_por_pagar)) 
            if not f.x_studio_folio_techra and not f.type=='out_refund' :
               worksheet.write(i, 13, f.residual)
            
            
            estado=dict(f._fields['state']._description_selection(self.env)).get(f.state)
            if f.type=='out_refund':
                tipoD='Nota de crédito'
            if f.type=='out_invoice':
                tipoD='Factura'   
            worksheet.write(i, 14, tipoD)
            try:
                if (f.x_studio_importacion=='pruebaNota' or f.x_studio_importacion=='lunes-19-10-2020' or f.x_studio_importacion=='lunes05' or f.x_studio_importacion=='viernes-30-10-2020' or f.x_studio_importacion=='lunes' or f.x_studio_importacion=='prueba' or f.x_studio_importacion=='martesGRupo') and f.state=='open':
                   worksheet.write(i, 15, f.x_studio_periodo_1.replace(' de ','/').upper())
                else:   
                  periodo=str(f.x_studio_periodo)
                  if periodo!='False':
                     worksheet.write(i, 15, periodo.replace(' de ','/').upper())
                  else:
                     if f.x_studio_field_EFIxP:
                          if  "-" in f.x_studio_field_EFIxP.x_studio_peridotmp  :
                            mes=f.x_studio_field_EFIxP.x_studio_peridotmp.split("-")[1]
                            comple=f.x_studio_field_EFIxP.x_studio_peridotmp.split("-")[0]
                            if mes =='01':
                                mes="ENERO"
                            if mes =='02':
                                mes="FEBRERO"
                            if mes =='03':
                                mes="MARZO"
                            if mes =='04':
                                mes="ABRIL"
                            if mes =='05':
                                mes="MAYO"
                            if mes =='06':
                                mes="JUNIO"
                            if mes =='07':
                                mes="JULIO"
                            if mes =='08':
                                mes="AGOSTO"
                            if mes =='09':
                                mes="SEPTIEMBRE"
                            if mes =='10':
                                mes="OCTUBRE"
                            if mes =='11':
                                mes="NOVIEMBRE"
                            if mes =='12':
                                mes="DICIEMBRE"
                            periodo=mes +"/"+comple
                          else:      
                            periodo=str(f.x_studio_field_EFIxP.x_studio_peridotmp.replace(' de ','/').upper()) 
                     worksheet.write(i, 15,periodo )

            except:
                worksheet.write(i, 15, f.x_studio_periodo_1) 
            
            
            if f.x_studio_ncs:
               worksheet.write(i, 16, str(f.x_studio_ncs))
            """
            else:
               worksheet.write(i, 16, '')
            """
            
            if str(f.x_studio_rep)!='False':
               worksheet.write(i, 17, str(f.x_studio_rep))
            else:
               worksheet.write(i, 17, '')
            worksheet.write(i, 18, str(f.x_studio_retencin))
            #worksheet.write(i, 19, str(f.x_studio_retencin))
            pagos=f.payment_ids
            pago=''
            banco=''
            cuentaO=''
            cuentaB=''
            estopago=''
            referencia=''
            fechapago=''
            
            for p in pagos:
                if p.l10n_mx_edi_cfdi_uuid:
                   pago+=str(p.l10n_mx_edi_cfdi_uuid)+'   '+pago
                if p.payment_date:
                   fechapago+=str(p.payment_date)+'   '+fechapago
                if p.journal_id.name:
                   banco+=str(p.journal_id.name)+'  '+banco
                if p.state:
                   estadoC=dict(p._fields['state']._description_selection(self.env)).get(p.state) 
                   estopago+=estadoC+'   '+estopago
                if p.partner_bank_account_id.acc_number:
                   cuentaO+=str(p.partner_bank_account_id.acc_number)+'   '+cuentaO
                if p.journal_id.name:
                   cuentaB+=str(p.journal_id.name)+'   '+cuentaB
                if p.communication:
                   referencia+=str(p.communication)+'   '+referencia
                
            #if str(f.partner_id.name)=='sin contacto':
            #    worksheet.write(i, 8, f.x_studio_cliente)
            #else:
            #    worksheet.write(i, 19, pago)
            if str(f.partner_id.name)=='sin contacto':
               worksheet.write(i, 20, f.x_studio_banco)
            else:
               worksheet.write(i, 20, banco) 
            
            worksheet.write(i, 21, cuentaO)
            
            worksheet.write(i, 22, cuentaB)
            
            if (f.x_studio_importacion=='pruebaNota' or f.x_studio_importacion=='lunes-19-10-2020' or f.x_studio_importacion=='lunes05' or f.x_studio_importacion=='viernes-30-10-2020' or f.x_studio_importacion=='lunes' or f.x_studio_importacion=='prueba' or f.x_studio_importacion=='martesGRupo') and f.state=='open':
               worksheet.write(i, 23, f.x_studio_folio_fiscal_pago_techra)
            else:
               if f.state=='paid': 
                  worksheet.write(i, 23, pago)
               if f.state=='cancel':
                  worksheet.write(i, 23, 'Cancelado')                   
               if f.state=='open':
                  worksheet.write(i, 23, estado)                        
                
                
            worksheet.write(i, 24, f.partner_id.x_studio_ejecutivo.name)
            worksheet.write(i, 25, f.partner_id.x_studio_vendedor.name)
            
            if str(f.partner_id.name)=='sin contacto':
               worksheet.write(i, 26, f.x_studio_referencia)
            else:
               worksheet.write(i, 26, referencia)
            
            if (f.x_studio_importacion=='pruebaNota' or f.x_studio_importacion=='lunes-19-10-2020' or f.x_studio_importacion=='lunes05' or f.x_studio_importacion=='viernes-30-10-2020' or f.x_studio_importacion=='lunes' or f.x_studio_importacion=='prueba' or f.x_studio_importacion=='martesGRupo') and f.state=='open':
               dater=''     
               dft=f.x_studio_fecha_de_pago
                
               if dft:
                  if 'CST' in dft:
                      datesr=datetime.datetime.strptime(dft, '%a %b %d %H:%M:%S CST %Y')
                  if 'CDT' in dft:  
                      datesr=datetime.datetime.strptime(dft, '%a %b %d %H:%M:%S CDT %Y')
               worksheet.write(i, 27, dater,format6)
               worksheet.write(i, 16, f.x_studio_nota)
               worksheet.write(i, 28, f.x_studio_pagos)
               dfy=f.x_studio_fecha_captura
               if dfy:
                  if 'CST' in dfy:
                      datesrC=datetime.datetime.strptime(dfy, '%a %b %d %H:%M:%S CST %Y')
                  if 'CDT' in dfy:  
                      datesrC=datetime.datetime.strptime(dfy, '%a %b %d %H:%M:%S CDT %Y')
                  worksheet.write(i, 29, datesrC,format6)
               if f.x_studio_fecha_comentario:
                  worksheet.write(i, 30, f.x_studio_fecha_comentario)
               if f.x_studio_oboservaciones:
                  worksheet.write(i, 31, f.x_studio_oboservaciones)
               if f.x_studio_usuario_cxc:
                  worksheet.write(i, 32, f.x_studio_usuario_cxc)
               worksheet.write(i, 24, f.x_studio_ejecutivo_atc)
               worksheet.write(i, 25, f.x_studio_ejecutivo_de_cuenta)
               
               if f.type=='out_refund':
                  if f.x_studio_folio_fiscal_pago_techra=='Cancelado':
                     worksheet.write(i, 33, 'C')
                  else:  
                     worksheet.write(i, 33,'NDC')
               else:
                  worksheet.write(i, 33, f.x_studio_estadohtml)                                    
            else:
               worksheet.write(i, 27, fechapago)
               if estado=='Pagado':
                  estado='P'
               if estado=='Abierto':
                  estado='NP'
               if estado=='Cancelado':
                  estado='C'
               worksheet.write(i, 33, estado)
            
            
            
            
            
            
            
            i=1+i
        
        
        """
        worksheet = workbook.add_worksheet('atrasados')
        content = ["Cliente","0 a 30 dias", "Folio 0 a 30 dias","31 a 45 dias ", "Folio 31 a 45 dias","46 a 60 ", "Folio 46 a 60","61 a 90","Folio 61 a 90"," mayor a 90","Folios mayores a 90"]
        bold = workbook.add_format({'bold': True})
        neg = workbook.add_format({'border': 2})
        i=0
        for item in content :           
            worksheet.write(0, i, item,neg)            
            #row += 1
            i=i+1
        
        i=1
        clientes_set=set()
        for cli in dir:
            if  str(cli.partner_id.name)=='sin contacto':
                clientes_set.add(cli.x_studio_cliente)
            else:    
                clientes_set.add(cli.partner_id.name)
        
        for cuenta in clientes_set :    
            facturasT=0
            foliosT=''
            facturasC=0
            foliosC=''
            facturasF=0
            foliosF=''
            facturasG=0
            foliosG=''
            facturasH=0
            foliosH=''
            
            hoy=date.today()
            for fecha in dir:
                #_logger.info("id lol"+str(fecha.id))
                dias=hoy-fecha.date_invoice
                if int(dias.days)<31:
                    if str(fecha.partner_id.name)=='sin contacto':
                       if cuenta==fecha.x_studio_cliente:
                            facturasT=facturasT+1
                            foliosT=str(fecha.number)+' '+foliosT        
                    if str(fecha.partner_id.name)==cuenta:    
                            facturasT=facturasT+1
                            foliosT=str(fecha.number)+' '+foliosT        
                
                if int(dias.days)>30 and int(dias.days)<46:
                    if str(fecha.partner_id.name)=='sin contacto':
                       if cuenta==fecha.x_studio_cliente:
                            facturasC=facturasC+1
                            foliosC=str(fecha.number)+' '+foliosC
                    if str(fecha.partner_id.name)==cuenta:    
                            facturasC=facturasC+1
                            foliosC=str(fecha.number)+' '+foliosC
                            
                if int(dias.days)>45 and int(dias.days)<61:
                    if str(fecha.partner_id.name)=='sin contacto':
                       if cuenta==fecha.x_studio_cliente:
                            facturasF=facturasF+1
                            foliosF=str(fecha.number)+' '+foliosF
                    if str(fecha.partner_id.name)==cuenta:    
                            facturasF=facturasF+1
                            foliosF=str(fecha.number)+' '+foliosF

                if int(dias.days)>60 and int(dias.days)<91:
                    if str(fecha.partner_id.name)=='sin contacto':
                       if cuenta==fecha.x_studio_cliente:
                            facturasG=facturasG+1
                            foliosG=str(fecha.number)+' '+foliosG
                    if str(fecha.partner_id.name)==cuenta:    
                            facturasG=facturasG+1
                            foliosG=str(fecha.number)+' '+foliosG

                if int(dias.days)>90:
                    if str(fecha.partner_id.name)=='sin contacto':
                       if cuenta==fecha.x_studio_cliente:
                            facturasH=facturasH+1
                            foliosH=str(fecha.number)+' '+foliosH
                    if str(fecha.partner_id.name)==cuenta:    
                            facturasH=facturasH+1
                            foliosH=str(fecha.number)+' '+foliosH            
                                         
                
            #facturas=0
            
            
            #worksheet.write(i, 0, str(fecha.date_invoice))
            #dias=date.today()-fecha.date_invoice
            #worksheet.write(i, 1, str(dias.days))
            
            worksheet.write(i, 0, cuenta)
            worksheet.write(i, 1, str(facturasT))
            worksheet.write(i, 2, foliosT)
            worksheet.write(i, 3, str(facturasC))
            worksheet.write(i, 4, foliosC)
            worksheet.write(i, 5, str(facturasF))
            worksheet.write(i, 6, foliosF)
            worksheet.write(i, 7, str(facturasG))
            worksheet.write(i, 8, foliosG)
            worksheet.write(i, 9, str(facturasH))
            worksheet.write(i, 10, foliosH)
            i=i+1
        
        
        """
        workbook.close()
        data = open('Example23.xlsx', 'rb').read()
        
        base64_encoded = base64.b64encode(data).decode('UTF-8')
        #data = base64.encodestring(data)
        attachment = {'name': 'Export Account Information',
        'datas': base64_encoded,
        'datas_fname': 'reporte de facturacion .xlsx',
        'res_model': 'account.invoice',
        'res_id': self.id}

        attachment_id = self.env['ir.attachment'].create(attachment)
        return {
        'type': 'ir.actions.act_url',
        'url': "web/content/?model=ir.attachment&id=" + str(attachment_id.id) +
        "&filename=accounts_export&field=datas&download=true&filename=" + attachment_id.datas_fname,
        'target': 'self',
        #'type': 'ir.actions.act_window'
        }
        
        #raise exceptions.ValidationError("faltan forma de pago para crear factura"+str(self.excelD))
