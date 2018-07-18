from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.addons.br_account.tests.test_base import TestBaseBr


class TestAccountInvoiceLine(TestBaseBr):

    def setUp(self):
        super(TestAccountInvoiceLine, self).setUp()

        analytic_account = self.env['account.analytic.account'].create({
            'name': 'test account',
        })

        # Should be changed by automatic on_change later
        invoice_account = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref('account.data_account_type_receivable').id)], limit=1).id
        invoice_line_account = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref('account.data_account_type_expenses').id)], limit=1).id

        invoice = self.env['account.invoice'].create({'partner_id': self.env.ref('base.res_partner_2').id,
                                                        'account_id': invoice_account,
                                                        'type': 'in_invoice',
                                                        })

        self.invoice_line = self.env['account.invoice.line'].create(
            {'product_id': self.env.ref('product.product_product_4').id,
                'quantity': 5.0,
                'price_unit': 100.0,
                'invoice_id': invoice.id,
                'name': 'product that cost 100',
                'account_id': invoice_line_account,
                'account_analytic_id': analytic_account.id,
                })

    def test__get_total_percentage(self):

        for line in self.invoice_line:
            line._get_total_percentage()
            self.assertEqual(line.margin_percentage, '-80.0 %')
