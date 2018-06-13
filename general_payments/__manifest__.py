{
    'name': 'Account Detached Payments',
    'summary': """Send and Receive your detached payments""",
    'version': '11.0.1.0.0',
    'category': 'Invoicing & Payments',
    'author': 'MultidadosTI',
    'license': 'LGPL-3',
    'website': 'http://www.multidadosti.com.br',
    'contributors': [
        'Michell Stuttgart <michellstut@gmail.com>',
        'Rodrigo Ferreira <rodrigosferreira91@gmail.com>',
    ],
    'depends': [
        'br_account_payment',
    ],
    'data': [
        'templates/assets.xml',
        'views/account_analytic.xml',
        'views/account_payment.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
