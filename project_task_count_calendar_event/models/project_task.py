from odoo import api, fields, models


class ProjectTask(models.Model):

    _inherit = 'project.task'

    event_number = fields.Integer(compute='_compute_event_number',
                                  string='Number of Meetings')

    @api.multi
    def _compute_event_number(self):
        """Contabiliza a quantidade de eventos de calendario
        relacionados a tarefa e que estão em aberto.
        """
        for task in self:
            cal_events = task.calendar_event_ids.filtered(
                lambda r: r.event_state == 'open')
            task.event_number = len(cal_events)

    @api.multi
    def action_make_meeting(self):
        """ Abre a visualização de calendário agendar um evento de 
        calendario relacionado ao projeto e tarefa atual.
        
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
            'search_default_task_id': self.id,
            'default_customer_partner_id': self.partner_id.id,
            'default_partner_ids': partners.ids,
            'default_user_id': self.env.uid,
            'default_name': self.name,
            'default_project_id': self.project_id.id,
            'default_task_id': self.id,
            'default_categ_ids': category and [category.id] or False,
        }

        return res
