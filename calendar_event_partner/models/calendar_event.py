from odoo import api, fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    @api.multi
    def get_company_partner(self):
        company = self.env['res.company']._company_default_get('calendar.event')  # noqa: 501
        return company.partner_id

    customer_partner_id = fields.Many2one(comodel_name='res.partner',
                                          string='Partner',
                                          track_visibility='onchange')

    company_partner_id = fields.Many2one(comodel_name='res.partner',
                                         default=get_company_partner)

    partner_name = fields.Char(compute='_compute_record_name')

    @api.depends('partner_id')
    def _compute_record_name(self):
        for rec in self:
            rec.partner_name = ' * ' + rec.customer_partner_id.name if rec.customer_partner_id else ''  # noqa: 501
