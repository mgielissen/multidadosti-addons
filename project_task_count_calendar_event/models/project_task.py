from odoo import api, fields, models


class ProjectTask(models.Model):

    _inherit = 'project.task'

    event_number = fields.Integer(compute='_compute_event_number',
                                  string='Number of Meetings')

    @api.multi
    def _compute_event_number(self):
        for record in self:
            cal_events = record.calendar_event_ids.filtered(
                lambda r: r.event_state == 'open')
            record.event_number = len(cal_events)

    @api.multi
    def action_make_meeting(self):
        """ This opens Meeting's calendar view to schedule meeting on
        current applicant
            @return: Dictionary value for created Meeting view
        """
        self.ensure_one()

        task_owner_id = self.env['res.users'].browse(self.env.uid)
        partners = task_owner_id.partner_id | self.user_id.partner_id

        category = self.env.ref('calendar.categ_meet1')

        res = self.env['ir.actions.act_window'].for_xml_id(
            'calendar', 'action_calendar_event')

        res['context'] = {
            'search_default_partner_ids': task_owner_id.name,
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
