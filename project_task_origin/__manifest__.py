{
    'name': 'Project Task Origin',
    'license': 'LGPL-3',
    'author': 'MultidadosTI',
    'version': '11.0.1.0.0',
    'website': 'www.multidadosti.com.br',
    'summary': """Sets the project task source ( issue or feature)""",
    'category': 'Project',
    'contributors': [
        'Rodrigo Ferreira <rodrigosferreira91@gmail.com>',
    ],
    'depends': [
        'project_kanban_onclick_redirect_project',
    ],
    'data': [
        'template/assets.xml',
        'views/project_task.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
