# -*- coding: utf-8 -*-
{
    'name': "Project Stock Modifications",

    'summary': """
        """,

    'description': """
    """,

    'author': "Ibrahim Abdultawab",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'stock', 'account', 'payment_receipt_voucher'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/project_views.xml',
        'views/account_views.xml',
        'views/voucher_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
