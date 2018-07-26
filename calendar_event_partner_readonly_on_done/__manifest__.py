{
    'name': 'Calendar Event Partner Readonly on Done',
    'version': '11.0.1.0.0',
    'author': 'MultidadosTI',
    'maintainer': 'MultidadosTI',
    'website': 'www.multidadosti.com.br',
    'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': 'Make partner readonly when calendar event is done',
    'contributors': [
        'Michell Stuttgart <michellstut@gmail.com>',
        'Rodrigo Ferreira <rodrigo.santos@multidadosti.com.br>',
    ],
    'depends': [
        'calendar_event_partner',
        'calendar_event_stage',
    ],
    'data': [
        'views/calendar_event.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
