{
    'name': 'Calendar Event Timesheet',
    'version': '11.0.1.0.0',
    'author': 'MultidadosTI',
    'maintainer': 'MultidadosTI',
    'website': 'www.multidadosti.com.br',
    'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': 'Create timesheet entry to calendar events',
    'contributors': [
        'Michell Stuttgart <michellstut@gmail.com>',
    ],
    'depends': [
        'analytic_base_field',
        'calendar_event_feedback',
        'calendar_event_partner_readonly_on_done',
        'calendar_event_project_readonly_on_done',
        'hr_timesheet_project_task_stage',
    ],
    'data': [
        'views/account_analytic_line.xml',
        'wizards/calendar_event_finish.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
