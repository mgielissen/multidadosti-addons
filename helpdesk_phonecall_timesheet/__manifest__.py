{
    'name': 'HelpDesk PhoneCall Timesheet',
    'license': 'LGPL-3',
    'author': 'MultidadosTI',
    'version': '11.0.1.0.0',
    'website': 'www.multidadosti.com.br',
    'summary': """Integration PhoneCall and Timesheet""",
    'category': 'Project',
    'contributors': [
        'Michell Stuttgart <michellstut@gmail.com>',
        'Rodrigo Ferreira <rodrigosferreira91@gmail.com>',
    ],
    'depends': [
        'hr_timesheet',
        'analytic_base_field',
        'helpdesk_phonecall_support',
    ],
    'data': [
        'wizards/helpdesk_phonecall_confirm.xml',
        'views/account_analytic_line.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
