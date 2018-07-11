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

    def _get_shared_move_line_vals(self, debit, credit, amount_currency,
                                   move_id, invoice_id=False):
        """
            Returns values common to both move lines (except for debit, credit
            and amount_currency which are reversed)
        """
        res = super(AccountPayment, self)._get_shared_move_line_vals(
            debit, credit, amount_currency, move_id, invoice_id=invoice_id)

        if self.invoice_ids:

            for inv in self.invoice_ids:
                self.analytic_account_id = \
                    inv.invoice_line_ids[0].account_analytic_id.id

        # if not self.invoice_ids:
        res['analytic_account_id'] = self.analytic_account_id.id
        res['partner_id'] = self.partner_id.id
        return res

    @api.constrains('destination_journal_id', 'journal_id')
    def _check_destination_journal_id(self):
        if self.destination_journal_id == self.journal_id:
            raise ValidationError(_(
                'You can not make a transfer to the same journal'))
