{
    'name': 'HR Timesheet Project Task Stage',
    'version': '11.0.1.0.0',
    'author': 'MultidadosTI',
    'maintainer': 'MultidadosTI',
    'website': 'www.multidadosti.com.br',
    'license': 'LGPL-3',
    'category': 'Timesheets',
    'summary': 'Use project task stage to filter stages in timesheet',
    'contributors': [
        'Aldo Soares <soares_aldo@hotmail.com>',
        'Michell Stuttgart <michellstut@gmail.com>',
    ],
    'depends': [
        'analytic_base_field',
        'sale_timesheet',
    ],
    'data': [
        'views/account_analytic_line.xml',
        'views/project_task.xml',
        'views/project_project.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
