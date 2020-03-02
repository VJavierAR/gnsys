# -*- coding: utf-8 -*-
{
    'name': "servicios_gnsys",

    'summary': """
        Servicios tipo gnsys""",

    'description': """
        Modelo de servicios tipo gnsys
    """,

    'author': "GNSYS",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
  'version': '12.0.1.0.0',
    # any module necessary for this one to work correctly
    'depends': [
        'stock',
        'sale',
        'product',
        'mail'
    ],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        #'security/servicios_security.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    #'demo': [
     #   'demo/demo.xml',
    #],
    'installable': True,
    'application': True,
    'auto_install': False,
}
