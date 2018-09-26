{
    'name': 'Project Task - Count Calendar Event',
    'version': '11.0.1.0.0',
    'author': 'MultidadosTI',
    'maintainer': 'MultidadosTI',
    'website': 'www.multidadosti.com.br',
    'license': 'LGPL-3',
    'category': 'Project',
    'summary': """Count meeting records at kanban view and
                creates new calendar events from project's task view form""",
    'contributors': [
        'Michell Stuttgart <michellstut@gmail.com>',
    ],
    'depends': [
        'project_task_calendar',
        'project_stage_state',
        'calendar_event_partner',
    ],
    'data': [
        'views/project_project.xml',
        'views/project_task.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
