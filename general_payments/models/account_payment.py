from datetime import datetime

from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    payment_amount_original = fields.Monetary(string='Original Value',
                                              readonly=True)

    general_account_id = fields.Many2one(comodel_name='account.account',
                                         string='Account')

    analytic_account_id = fields.Many2one('account.analytic.account',
                                          string='Analytic Account')

    description = fields.Text(string='Description')

    def _get_launch_move_values(self):
        """Generates a proper dict containing move values to create a launch
        move record through 'account.payment' record creation.
        
        Returns:
            dict -- Dict containing values to create an 'account.move' record
        """
        is_payment = True if self.payment_type == 'inbound' else False

        payment_part_name = (_('Payment') if is_payment else _('Receivement'))
        partner_part_name = (_('Customer') if self.partner_type == 'customer'
            else _('Supplier'))

        name = '%s - %s' % (payment_part_name, partner_part_name)

        date_now = datetime.strftime(datetime.now(), '%Y-%m-%d')

        account_move_lines_base_dict = {
            'partner_id': self.partner_id.id,
            'date_maturity': date_now,
        }

        ml_debit = {
            **account_move_lines_base_dict,
            'debit': self.amount,
        }
        ml_credit = {
            **account_move_lines_base_dict,
            'credit': self.amount,
        }

        if is_payment:
            move_account = self.partner_id.property_account_receivable_id
            ml_debit['name'] = name
            ml_debit['account_id'] = move_account.id
            ml_debit['analytic_account_id'] = self.analytic_account_id.id
            ml_credit['account_id'] = self.general_account_id.id
        else:
            move_account = self.partner_id.property_account_payable_id
            ml_credit['name'] = name
            ml_credit['account_id'] = move_account.id
            ml_credit['analytic_account_id'] = self.analytic_account_id.id
            ml_debit['account_id'] = self.general_account_id.id

        # Create account.move dict
        move_values = {
            'name': self._get_journal_entry_name(self.journal_id, date_now),
            'journal_id': self.journal_id.id,
            'account_id': move_account.id,
            'date': date_now,
            'line_ids': [(0, 0, ml_credit), (0, 0, ml_debit)],
        }

        return move_values

    @api.multi
    def post(self):
        for rec in self:
            # Valid only in receivement('outbound') or payment('inbound')
            is_financial_move = self.env.context.get('financial_move', False)
            if rec.payment_type != 'transfer' and is_financial_move:
                # Creates the 'launch' move record to link with payment move 
                # generated through 'account.payment' record creation
                move_values = rec._get_launch_move_values()
                move = self.env['account.move'].create(move_values)
                move.post()
                rec.write({
                    'move_id': move.id,
                    'payment_amount_original': move.amount,
                })
                # Calls super method as if it had been called in 'account.move'
                # view.
                ctx = {
                    'active_model': 'account.move',
                }
                super(AccountPayment, rec).with_context(ctx).post()
            else:
                rec.payment_amount_original = rec.move_id.amount
                super(AccountPayment, rec).post()

    @api.multi
    def reverse(self):
        for rec in self:
            # Option available only in payments which no relation with titles.
            if not rec.invoice_ids:
                reconcile_move = self.env['account.move.line'].search(
                    [('payment_id', '=', rec.id),
                    ('move_id', '!=', rec.move_id.id)], limit=1).move_id
                
                # Deletes reconcile records(account.partial.reconcile).
                for line in rec.move_line_ids:
                    line.matched_credit_ids.unlink()
                    line.matched_debit_ids.unlink()

                # Deletes the proper launch move record.
                reconcile_move.button_cancel()
                reconcile_move.unlink()
                # Deletes the proper payment move record.
                rec.move_id.button_cancel()
                rec.move_id.unlink()
                # Turns the payment state to draft
                rec.action_draft()

    @staticmethod
    def _get_journal_entry_name(journal, date):
        """Generates a name, based in sequence used in 'journal' param related,
        and date param.
        
        Arguments:
            journal {object} -- Account journal record.
            date {str} -- Processing date of record.
        
        Raises:
            UserError -- Journal record must have sequence active.
        
        Returns:
            str -- Name which will be used in title
        """
        if not journal.sequence_id.active:
            raise UserError(_(
                'Please activate the sequence of selected '
                'journal!'))

        # Get sequence of journal
        return journal.sequence_id.with_context(
            ir_sequence_date=str(date)).next_by_id()

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
