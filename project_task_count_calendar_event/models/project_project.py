from odoo import api, fields, models
from odoo.tools.translate import _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    event_number = fields.Integer(compute='_compute_event_number',
                                  string='Number of Meetings')

    label_tasks = fields.Char(translate=True,
                              default=lambda self: _("Tasks"),
                              help="Gives label to tasks on project's kanban "
                                   "view.")

    label_issues = fields.Char(translate=True,
                               default=lambda self: _("Issues"))

    def _compute_task_count(self):
        """Contabiliza a quantidade de tarefas do projeto. As 
        tarefas finalizadas ou cancelas não são contabilizadas.
        """
        for project in self:
            part = project.task_ids.filtered(
                lambda r: r.state not in ['done', 'cancelled'])
            project.task_count = len(part)

    @api.multi
    def _compute_event_number(self):
        """Contabiliza a quantidade de eventos de calendario
        relacionados ao projeto e que estão em aberto.
        """
        for project in self:
            cal_events = project.calendar_event_ids.filtered(
                lambda r: r.event_state == 'open')
            project.event_number = len(cal_events)

    @api.multi
    def action_make_meeting(self):
        """ Abre a visualização de calendário agendar um evento de 
        calendario relacionado ao projeto atual.
        
        Returns:
            dict -- ir.actions.act_window que redirecion para tela do calendario.
        """
        self.ensure_one()

        partners = self.env.user.partner_id | self.user_id.partner_id

        category = self.env.ref('calendar.categ_meet1')

        res = self.env['ir.actions.act_window'].for_xml_id(
            'calendar', 'action_calendar_event')

        res['context'] = {
            'search_default_partner_ids': self.env.user.name,
            'search_default_project_id': self.id,
            'default_customer_partner_id': self.partner_id.id,
            'default_partner_ids': partners.ids,
            'default_user_id': self.env.uid,
            'default_name': self.name,
            'default_project_id': self.id,
            'default_categ_ids': category and [category.id] or False,
        }

        return res
