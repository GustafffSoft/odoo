# -*- coding: utf-8 -*-
{
    'name': "cositas_dulces",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'hr', 'mail', 'calendario_unificado'],

    # always loaded
    'data': [
        'data/project_data.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/ir_cron.xml',
        'data/email_template.xml',
        'data/email_template_prueba.xml',
        'data/ir_cron_prueba.xml',

    ],
    'post_init_hook': 'post_init_hook',
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

