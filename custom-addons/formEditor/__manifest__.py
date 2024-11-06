{
    'name': 'Form Editor Integration',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Integration with Form Editor API',
    'description': """
        This module integrates with the Form Editor API to import and manage templates and their results.
    """,
    'author': 'Your Name',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/template_views.xml',
        'views/question_views.xml',
        'wizard/import_results_wizard_view.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}