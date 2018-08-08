import datetime

from odoo import api, models


class HelpDeskPhoneCallConfirm(models.TransientModel):
    _inherit = 'helpdesk.phonecall.confirm'
    _description = 'Wizard to confirm phonecall'

    @api.multi
    def action_confirm_finish_phonecall(self):
        ret = super(HelpDeskPhoneCallConfirm,
                    self).action_confirm_finish_phonecall()

        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for rec in self.env['helpdesk.phonecall.service'].browse(active_ids):
            dt = datetime.datetime.strptime(rec.start_date_hour,
                                            '%Y-%m-%d %H:%M:%S')

            fmt = '%Y-%m-%d %H:%M:%S'
            d1 = datetime.datetime.strptime(rec.start_date_hour, fmt)
            d2 = datetime.datetime.strptime(rec.finish_date_hour, fmt)

            # Convert total seconds in hours in decimal format
            # When load the float field in screen, the widget
            # 'float_time' will go show time in to HH:MM format
            hours_diff_decimal = (d2 - d1).total_seconds() / 3600.0

            values = {
                'name': rec.description,
                'date': dt.date(),
                'user_id': rec.user_id.id,
                'customer_partner_id': rec.partner_id.id,
                'helpdesk_id': rec.id,
                'company_id': rec.company_id.id,
                'project_id': rec.project_id.id,
                'unit_amount': hours_diff_decimal,
            }

            self.env['account.analytic.line'].create(values)

        return ret
