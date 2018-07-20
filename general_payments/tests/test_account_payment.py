# -*- coding: utf-8 -*-
from unittest import mock

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools.translate import _


class TestAccountPayment(TransactionCase):
    def setUp(self):
        super(TestAccountPayment, self).setUp()
        self.main_company = self.env.ref('base.main_company')
        self.currency_real = self.env.ref('base.BRL')

        self.customer_receivable_account = self.env['account.account'].create({
            'code': '1.0.0',
            'name': 'Receivables Account - Customer',
            'user_type_id': self.env.ref(
                'account.data_account_type_receivable').id,
            'company_id': self.main_company.id,
            'reconcile': True,
        })

        self.supplier_payable_account = self.env['account.account'].create({
            'code': '2.0.0',
            'name': 'Payable Account - Supplier',
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
            'company_id': self.main_company.id,
            'reconcile': True,
        })

        self.revenue_account = self.env['account.account'].create({
            'code': '3.0.0',
            'name': 'Sale Revenues',
            'user_type_id': self.env.ref(
                'account.data_account_type_revenue').id,
            'company_id': self.main_company.id,
            'reconcile': True,
        })

        self.expense_account = self.env['account.account'].create({
            'code': '4.0.0',
            'name': 'Sale Expenses',
            'user_type_id': self.env.ref(
                'account.data_account_type_expenses').id,
            'company_id': self.main_company.id,
            'reconcile': True,
        })

        self.bank_account = self.env['account.account'].create({
            'code': '1.1.1.X',
            'name': 'Bank Account',
            'user_type_id': self.env.ref(
                'account.data_account_type_liquidity').id,
            'company_id': self.main_company.id,
        })

        self.other_bank_account = self.env['account.account'].create({
            'code': '1.1.1.Y',
            'name': 'Other Bank Account',
            'user_type_id': self.env.ref(
                'account.data_account_type_liquidity').id,
            'company_id': self.main_company.id,
        })

        self.customer = self.env['res.partner'].create({
            'name': 'Customer Name',
            'is_company': False,
            'customer': True,
            'supplier': False,
            'property_account_receivable_id': self.customer_receivable_account.id,
            'property_account_payable_id': self.supplier_payable_account.id,
        })

        self.supplier = self.env['res.partner'].create({
            'name': 'Supplier Name',
            'is_company': False,
            'customer': False,
            'supplier': True,
            'property_account_receivable_id': self.customer_receivable_account.id,
            'property_account_payable_id': self.supplier_payable_account.id,
        })

        self.journalrec_bank = self.env['account.journal'].create({
            'name': 'Bank',
            'code': 'BNK',
            'type': 'bank',
            'update_posted': True,
            'default_debit_account_id': self.bank_account.id,
            'default_credit_account_id': self.bank_account.id,
        })

        self.other_journalrec_bank = self.env['account.journal'].create({
            'name': 'Other Bank',
            'code': 'OTBNK',
            'type': 'bank',
            'default_debit_account_id': self.other_bank_account.id,
            'default_credit_account_id': self.other_bank_account.id,
        })

        self.customer_method_id = self.env['account.payment.method'].search([
            ('payment_type', '=', 'inbound')])[0]

        self.supplier_method_id = self.env['account.payment.method'].search([
            ('payment_type', '=', 'outbound')])[0]

        self.payment_transfer = self.env['account.payment'].create({
            'partner_type': 'supplier',
            'payment_type': 'transfer',
            'payment_method_id': self.env.ref(
                'account.account_payment_method_manual_out').id,
            'journal_id': self.journalrec_bank.id,
            'partner_id': self.customer.id,
            'amount': 500.00,
            'destination_journal_id': self.other_journalrec_bank.id,
            'payment_date': '2018-02-22',
        })

        self.analytic_account = self.env['account.analytic.account'].create({
            'name': 'Analytic Account',
        })

        self.analytic_tag = self.env['account.analytic.tag'].create({
            'name': 'Analytic Tag',
        })

        self.customer_payment = self.env['account.payment'].create({
            'partner_type': 'customer',
            'payment_type': 'inbound',
            'analytic_account_id': self.analytic_account.id,
            'analytic_tag_ids': [(6, 0, [self.analytic_tag.id])],
            'general_account_id': self.revenue_account.id,
            'payment_method_id': self.customer_method_id.id,
            'journal_id': self.journalrec_bank.id,
            'partner_id': self.customer.id,
            'amount': 500.00,
        })

        self.supplier_payment = self.env['account.payment'].create({
            'partner_type': 'supplier',
            'payment_type': 'outbound',
            'analytic_account_id': self.analytic_account.id,
            'analytic_tag_ids': [(6, 0, [self.analytic_tag.id])],
            'general_account_id': self.expense_account.id,
            'payment_method_id': self.supplier_method_id.id,
            'journal_id': self.journalrec_bank.id,
            'partner_id': self.supplier.id,
            'amount': 500.00,
        })

    def _get_line_from_move_dict(self, vals, relative=True):
        """Gets the relative line values which represents move operation, or 
        the other balancing line, depending on 'relative' param value.
        
        Arguments:
            vals {dict} -- Dict values to create an account.move record.
            relative {bool} -- Used to select proper line to return.
        
        Returns:
            dict -- Dict values to create an account.move.line record.
        """
        for line in vals['line_ids']:
            if line[2]['account_id'] == vals['account_id']:
                return line[2]

    def test__check_destination_journal_id(self):
        with self.assertRaises(ValidationError):
            self.payment_transfer.destination_journal_id = (
                self.payment_transfer.journal_id)
            self.assertTrue(
                self.payment_transfer._check_destination_journal_id())

    def test__get_launch_move_values(self):
        customer_vals = self.customer_payment._get_launch_move_values()

        self.assertEqual(customer_vals['account_id'],
                         self.customer_receivable_account.id)
        self.assertEqual(customer_vals['journal_id'],
                         self.customer_payment.journal_id.id)

        customer_line = self._get_line_from_move_dict(customer_vals)

        self.assertEqual(customer_line['name'],
                         '%s - %s' % (_('Payment'), _('Customer')))
        self.assertEqual(customer_line['debit'], self.customer_payment.amount)
        self.assertEqual(customer_line['partner_id'], self.customer.id)
        self.assertEqual(customer_line['account_id'],
                         self.customer_receivable_account.id)

        customer_balance_line = self._get_line_from_move_dict(
            customer_vals, False)

        self.assertEqual(customer_balance_line['account_id'],
                         self.customer_receivable_account.id)

        supplier_vals = self.supplier_payment._get_launch_move_values()

        self.assertEqual(supplier_vals['account_id'],
                         self.supplier_payable_account.id)
        self.assertEqual(supplier_vals['journal_id'],
                         self.supplier_payment.journal_id.id)

        supplier_line = self._get_line_from_move_dict(supplier_vals)

        self.assertEqual(supplier_line['name'],
                         '%s - %s' % (_('Receivement'), _('Supplier')))
        self.assertEqual(supplier_line['credit'], self.supplier_payment.amount)
        self.assertEqual(supplier_line['partner_id'], self.supplier.id)
        self.assertEqual(supplier_line['account_id'],
                         self.supplier_payable_account.id)

        supplier_balance_line = self._get_line_from_move_dict(
            supplier_vals, False)

        self.assertEqual(supplier_balance_line['account_id'],
                         self.supplier_payable_account.id)
    
    def test__get_liquidity_launch_aml_vals(self):
        res = self.customer_payment._get_liquidity_launch_aml_vals(
            is_payment=True)

        self.assertEqual(
            res['account_id'], self.customer_receivable_account.id)
        self.assertEqual(
            res['name'], '%s - %s' % (_('Customer'), _('Revenue')))

        res = self.customer_payment._get_liquidity_launch_aml_vals(
            is_payment=False)

        self.assertEqual(
            res['account_id'], self.supplier_payable_account.id)
        self.assertEqual(
            res['name'], '%s - %s' % (_('Customer'), _('Expense')))

        res = self.supplier_payment._get_liquidity_launch_aml_vals(
            is_payment=False)

        self.assertEqual(
            res['account_id'], self.supplier_payable_account.id)
        self.assertEqual(
            res['name'], '%s - %s' % (_('Supplier'), _('Expense')))

        res = self.supplier_payment._get_liquidity_launch_aml_vals(
            is_payment=True)

        self.assertEqual(
            res['account_id'], self.customer_receivable_account.id)
        self.assertEqual(
            res['name'], '%s - %s' % (_('Supplier'), _('Revenue')))
    
    def test__get_counterpart_launch_aml_vals(self):
        res = self.customer_payment._get_counterpart_launch_aml_vals()
        self.assertEqual(res['account_id'], self.revenue_account.id)

        res = self.supplier_payment._get_counterpart_launch_aml_vals()
        self.assertEqual(res['account_id'], self.expense_account.id)

    def test__get_liquidity_account(self):
        acc_id = self.customer_payment._get_liquidity_account(is_payment=True)
        self.assertEqual(acc_id, self.customer_receivable_account.id)

        acc_id = self.customer_payment._get_liquidity_account(is_payment=False)
        self.assertEqual(acc_id, self.supplier_payable_account.id)

    @mock.patch('odoo.addons.general_payments.models.account_payment.'
                'AccountPayment._get_liquidity_launch_aml_vals')
    @mock.patch('odoo.addons.general_payments.models.account_payment.'
                'AccountPayment._get_counterpart_launch_aml_vals')
    def test__get_launch_aml_vals(self, _get_liquidity_launch_aml_vals,
        _get_counterpart_launch_aml_vals):
        
        self.customer_payment._get_launch_aml_vals(
            is_payment=True, is_debit_line=True)
        self.customer_payment._get_launch_aml_vals(
            is_payment=True, is_debit_line=False)
        self.customer_payment._get_launch_aml_vals(
            is_payment=False, is_debit_line=True)
        self.customer_payment._get_launch_aml_vals(
            is_payment=False, is_debit_line=False)

        self.assertEqual(
            len(_get_liquidity_launch_aml_vals.mock_calls), 2)
        self.assertEqual(
            len(_get_counterpart_launch_aml_vals.mock_calls), 2)

    def test_post(self):
        ctx = {
            'financial_move': True,
        }
        self.supplier_payment.with_context(ctx).post()
        # Exist an 'account.move' record assigned ?
        self.assertTrue(self.supplier_payment.move_id)
        self.assertEqual(len(self.env['account.move'].search([])), 2)

        self.supplier_payment.move_id.compute_amount_residual()
        # The 'account.move' record have been reconciled with another 
        # 'account.move' record ?
        self.assertEqual(self.supplier_payment.move_id.paid_status, 'paid')

    def test_reverse(self):
        ctx = {
            'financial_move': True,
        }
        self.supplier_payment.with_context(ctx).post()
        # Two move records must be created
        self.assertEqual(len(self.env['account.move'].search([])), 2)

        self.supplier_payment.reverse()
        self.assertEqual(len(self.env['account.move'].search([]).ids), False)

        self.assertEqual(self.supplier_payment.state, 'draft')

    def test__onchange_payment_type(self):
        res = self.payment_transfer._onchange_payment_type()
        # Payments records which have type assigned as 'transfer', not is shown
        # in view, so, it is not necessary to define a domain in this field.
        self.assertNotIn('general_account_id', res['domain'])

        # Supplier payments must have an expense account attached (code 4)
        res = self.supplier_payment._onchange_payment_type()
        self.assertIn('general_account_id', res['domain'])
        self.assertEqual(
            res['domain']['general_account_id'], [('code_first_digit', '=', 4)]
        )

        # Customer payments must have an revenue account attached (code 3)
        res = self.customer_payment._onchange_payment_type()
        self.assertIn('general_account_id', res['domain'])
        self.assertEqual(
            res['domain']['general_account_id'], [('code_first_digit', '=', 3)]
        )
