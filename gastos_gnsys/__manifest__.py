# -*- coding: utf-8 -*-
{
    #Nombre de modelo
    'name': "gastos_gnsys",

    'summary': """
        Gastos de GnSys""",

    'description': """
        Modelo de gastos de tipo GnSyS
    """,

    'author': "GNSYS",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
  'version': '12.0.1.0.0',
    # any module necessary for this one to work correctly
    #Modelo de dep
    'depends': [
        'mail',
        'hr',
        'helpdesk'
        
    ],

    # always loaded
    #Algunos de modelo (Csi todas son vistas)
    'data': [
        #'security/ir.model.access.csv',
        #'security/gastos_security.xml',
        'views/views.xml',
        'views/templates.xml',
        'wizard/wizard.xml',
        'report/report.xml'
    ],
    'qweb': ['static/src/xml/tree_view_button.xml'],
    # only loaded in demonstration mode
    #'demo': [
     #   'demo/demo.xml',
    #],
    'installable': True,
    'application': True,
    'auto_install': False,
}
