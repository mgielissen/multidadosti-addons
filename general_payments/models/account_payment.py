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

    analytic_account_id = fields.Many2one(string='Analytic Account',
                                          comodel_name='account.analytic.account')

    analytic_tag_ids = fields.Many2many(string='Analytic Tags',
                                        comodel_name='account.analytic.tag')

    description = fields.Text(string='Description')

    def _get_launch_move_values(self):
        """Generates a proper dict containing move values to create a launch
        move record through 'account.payment' record creation.
        
        Returns:
            dict -- Dict containing values to create an 'account.move' record
        """
        is_payment = True if self.payment_type == 'inbound' else False

        date_now = datetime.strftime(datetime.now(), '%Y-%m-%d')

        account_move_lines_base_dict = {
            'partner_id': self.partner_id.id,
            'date_maturity': date_now,
        }

        ml_debit = {
            **account_move_lines_base_dict,
            'debit': self.amount,
            **self._get_launch_aml_vals(is_payment, is_debit_line=True),
        }
        ml_credit = {
            **account_move_lines_base_dict,
            'credit': self.amount,
            **self._get_launch_aml_vals(is_payment, is_debit_line=False),
        }

        # Create account.move dict
        move_values = {
            'journal_id': self.journal_id.id,
            'account_id': self._get_liquidity_account(is_payment),
            'date': date_now,
            'line_ids': [(0, 0, ml_credit), (0, 0, ml_debit)],
        }

        return move_values
    
    def _get_liquidity_launch_aml_vals(self, is_payment):
        """Generates a proper dict containing aml values to create the 
        liquidity move line record through 'account.payment' record creation.
        
        Arguments:
            is_payment {bool} -- Verifies if the record is launching an expense
                or a revenue
        
        Returns:
            dict -- AML Liquidity values
        """
        return {
            'name': self._get_liquidity_launch_aml_name(is_payment),
            'account_id': self._get_liquidity_account(is_payment),
            'analytic_account_id': self.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        }
    
    def _get_liquidity_launch_aml_name(self, is_payment):
        """Generates a proper name to liquidity move line record which will be 
        created through 'account.payment' record creation.
        
        Arguments:
            is_payment {bool} -- Verifies if the record is launching an expense
                or a revenue
        
        Returns:
            str -- AML Liquidity name
        """
        if is_payment:
            payment_part_name = _('Revenue')
        else:
            payment_part_name = _('Expense')

        partner_part_name = (_('Customer') if self.partner_type == 'customer'
                             else _('Supplier'))
        return '%s - %s' % (partner_part_name, payment_part_name)

    def _get_counterpart_launch_aml_vals(self):
        """Generates a proper dict containing aml values to create the 
        counterpart move line record through 'account.payment' record creation.
        
        Returns:
            dict -- AML Liquidity values
        """
        return {
            'account_id': self.general_account_id.id,
        }
    
    def _get_liquidity_account(self, is_payment):
        if is_payment:
            return self.partner_id.property_account_receivable_id.id
        else:
            return self.partner_id.property_account_payable_id.id

    def _get_launch_aml_vals(self, is_payment, is_debit_line):
        # Depending on 'is_payment' value, will return dict of payment move
        # values or receivement move values to balance the payment record
        if (is_debit_line and is_payment) or (
            not is_debit_line and not is_payment):
            return self._get_liquidity_launch_aml_vals(is_payment)
        else:
            return self._get_counterpart_launch_aml_vals()

    @api.multi
    def post(self):
        
        context = dict(self._context or {})
        # Valid only in receivement('outbound') or payment('inbound')
        ctx_move = context.get('financial_move', False)
        active_model = context.get('active_model', False)
        is_financial_move = (
            True if ctx_move and active_model != 'account.move' else False)

        for rec in self:
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
            else:
                rec.payment_amount_original = rec.move_id.amount
        super(AccountPayment, self).post()

    @api.multi
    def cancel(self):
        for rec in self:
            # Deletes reconcile records(account.partial.reconcile).
            for line in rec.move_line_ids:
                line.matched_credit_ids.unlink()
                line.matched_debit_ids.unlink()
                
            if not rec.invoice_ids:
                liquidity_move = self.env['account.move.line'].search(
                    [('payment_id', '=', rec.id),
                    ('move_id', '!=', rec.move_id.id)], limit=1).move_id
                # Deletes the proper liquidity move record.
                liquidity_move.button_cancel()
                liquidity_move.unlink()
                # Deletes the proper launch move record.
                rec.move_id.button_cancel()
                rec.move_id.unlink()

            # Turns the payment state to cancel
            super(AccountPayment, rec).cancel()
            rec.move_name = False
    
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
