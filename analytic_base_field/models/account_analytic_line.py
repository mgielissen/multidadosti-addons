from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    customer_partner_id = fields.Many2one('res.partner',
                                          string='Customer Partner')
