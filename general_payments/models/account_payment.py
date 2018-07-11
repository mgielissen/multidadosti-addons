from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    general_account_id = fields.Many2one(comodel_name='account.account',
                                         string='Account')

    analytic_account_id = fields.Many2one('account.analytic.account',
                                          string='Analytic Account')

    description = fields.Text(string='Description')

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        res = super(AccountPayment, self)._onchange_payment_type()
        if not self.invoice_ids and not self.payment_type == 'transfer':
            # Set account_account prefix
            if self.payment_type == 'inbound':
                account_prefix = 3
            elif self.payment_type == 'outbound':
                account_prefix = 4

            res['domain']['general_account_id'] = [
                ('code_first_digit', '=', account_prefix)]

        return res

    @api.constrains('destination_journal_id', 'journal_id')
    def _check_destination_journal_id(self):
        if self.destination_journal_id == self.journal_id:
            raise ValidationError(_(
                'You can not make a transfer to the same journal'))
