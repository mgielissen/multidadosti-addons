import datetime

from odoo import api, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class CalendarEventFinish(models.TransientModel):
    _inherit = 'calendar.event.finish'

    @api.multi
    def action_finish_calendar_event(self):
        """Finaliza evento de calendário e cria entrada na planilha
        de horas (account.analytic.line).
        
        Raises:
            UserError -- quando o evento não possui projeto e/ou já esta finalizado.
        
        Returns:
            dict -- dict contendo 'ir.actions.act_window_close'.
        """

        self.ensure_one()
        res = super(CalendarEventFinish, self).action_finish_calendar_event()

        ce = self.calendar_event_id

        if ce.project_id and ce.event_state == 'done':
            dt = datetime.datetime.strptime(ce.start_datetime,
                                            '%Y-%m-%d %H:%M:%S')

            partners = [item.id for item in ce.partner_ids
                        if item.parent_id == ce.company_partner_id]

            users = self.env['res.users'].search([('partner_id', 'in', partners)])

            # Create Timesheet to any user in users list
            for user in users:
                values = self._get_account_analytic_line_values(
                    user=user, calendar_event=ce, start_datetime=dt)

                # Utilizamos sudo a fim de permitir que um usuario
                # crie entradas para outros usuarios
                self.env['account.analytic.line'].sudo().create(values)
        else:
            raise UserError(_("To finish this event, it must be in 'Open' "
                              "state and select a project"))

        return res

    @api.multi
    def _get_account_analytic_line_values(self, user, calendar_event, start_datetime):
        """Retorna valores para serem usados na criação de uma entrada na planilha
        de dados (account.analytic.line).

        Arguments:
            user {res.users} -- Usuario cujo entrada sera atribuida.
            calendar_event {calendar.event} -- Calendar Event para ser usado na entrada.
            start_datetime {datetime} -- objeto datetime com data e hora do evento.

        Returns:
            dict -- Dict com valores da account.analytic.entry.
        """

        self.ensure_one()
        values = {
            'name': calendar_event.name,
            'date': start_datetime.date(),
            'user_id': user.id,
            'customer_partner_id': calendar_event.customer_partner_id.id,
            'company_id': calendar_event.user_id.company_id.id,
            'project_id': calendar_event.project_id.id,
            'unit_amount': calendar_event.event_duration,
            'calendar_event_id': calendar_event.id,
        }

        if calendar_event.task_id:
            values['task_id'] = calendar_event.task_id.id
            values['project_task_type_id'] = calendar_event.task_id.stage_id.id

        return values
