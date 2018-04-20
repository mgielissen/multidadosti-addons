
{
    'name': 'Partner Activity Branch',
    'version': '11.0.1.0.0',
    'author': 'MultidadosTI',
    'maintainer': 'MultidadosTI',
    'website': 'www.multidadosti.com.br',
    'license': 'LGPL-3',
    'category': 'Base',
    'summary': 'Activity Branch for Partner',
    'contributors': [
        'Rodrigo Ferreira <rodrigosferreira91@gmail.com>',
    ],
    'depends': [
        'base',
        'account_replace_invoice_menu_sale',
        'tko_contacts',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/base_partner_activity_branch.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
