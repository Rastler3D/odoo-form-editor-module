# -*- coding: utf-8 -*-
{
    'name': 'Form Editor',
    'version': '1.0',
    'category': 'Custom',
    'summary': 'Integration with Form Editor',
    'description': """
        This module integrates with the Form Editor to import and manage templates and their results.
    """,
    'author': 'Rastler3D',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/template_views.xml',
        'views/menu_views.xml',
        'wizard/import_results_wizard_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}