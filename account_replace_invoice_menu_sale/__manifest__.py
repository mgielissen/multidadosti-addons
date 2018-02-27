{
    'name': 'Account Replace Invoice Menu in Sale',
    'version': '11.0.1.0.0',
    'author': 'MultidadosTI',
    'maintainer': 'MultidadosTI',
    'website': 'www.multidadosti.com.br',
    'license': 'LGPL-3',
    'category': 'Tools',
    'summary': """Account Replace Invoice Menu in Sale.""",
    'contributors': [
        'Michell Stuttgart <michellstut@gmail.com>',
        'Rodrigo Ferreira <rodrigosferreira91@gmail.com>',
    ],
    'depends': [
        'account_replace_invoice_menu',
        'sale',
        'sales_team',
        'tko_contacts',
    ],
    'data': [
        'views/sale.xml',
        'views/crm_team_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
