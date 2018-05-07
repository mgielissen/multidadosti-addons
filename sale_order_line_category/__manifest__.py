{
    'name': 'Sale Order Line Category',
    'version': '11.0.1.0.0',
    'author': 'MultidadosTI',
    'website': 'www.multidadosti.com.br',
    'license': 'LGPL-3',
    'category': 'Sale',
    'summary': 'Create categories of order line.',
    'contributors': [
        'Rodrigo Ferreira <rodrigosferreira91@gmail.com>',
    ],
    'depends': [
        'sale',
        'crm',
    ],
    'data': [
        'views/sale_order_line_category.xml',
        'views/sale_order.xml',
        'security/ir.model.access.csv'
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}
