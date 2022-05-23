# -*- coding: utf-8 -*-
{
    'name': "Payment & Receipt Voucher",

    'summary': """
        """,

    'description': """
    """,

    'author': "Eng.Ibrahim Abdultawab",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_accountant', 'account'],

    # always loaded
    'data': [
        'security/voucher_security.xml',
        'data/data.xml',
        'security/ir.model.access.csv',
        'reports/reports.xml',
        'reports/account_voucher_report.xml',
        'views/voucher_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
