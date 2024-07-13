# -*- coding: utf-8 -*-
{
    'name': "calendario_unificado",

    'summary': "Modulo para la gestion de  los empleados pertenecientes a proyestos SEFI y PE",

    'description': """
Long description of module's purpose
    """,

    'author': "Ernesto Rodolfo Castañeda Squires",
    'website': "https://www.sisinfo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'project', 'calendar', ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/project_data.xml',
        'data/ir_cron_calculo_presencialidad.xml',

        'views/empleado_sefipe.xml',
        'views/hr_comentarios_date.xml',
        'views/hr_important_date.xml',
        'views/project_task.xml',
        'views/visualizacion.xml',
        # 'views/licencias.xml',


        'views/menu_item.xml',

        # 'views/pagos.xml',
    ],
    'license': 'LGPL-3',

    'assets': {
        'web.assets_frontend': [
            'hr_proyectos_especiales/static/src/css/custom_calendar.css',
        ],
    },
}
