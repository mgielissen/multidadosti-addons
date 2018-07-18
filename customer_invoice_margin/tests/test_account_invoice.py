from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.addons.br_account.tests.test_base import TestBaseBr


class TestAccountInvoice(TestBaseBr):

    def setUp(self):
        super(TestAccountInvoice, self).setUp()

        self.main_company = self.env.ref('base.main_company')

        partner = self.env['res.partner'].create({
            'name': 'Nome Empresa',
            'is_company': True,
            'property_account_receivable_id': self.receivable_account.id,
        })

        self.journalrec = self.env['account.journal'].create({
            'name': 'Faturas',
            'code': 'INV',
            'type': 'sale',
            'update_posted': True,
            'default_debit_account_id': self.revenue_account.id,
            'default_credit_account_id': self.revenue_account.id,
        })

        invoice_line_data = [
            (0, 0,
             {
                 'product_id': self.service.id,
                 'quantity': 10.0,
                 'price_unit': 25.0,
                 'account_id': self.revenue_account.id,
                 'name': 'product test 5',
                 'product_type': self.service.fiscal_type,
             }
             )
        ]

        invoice_values = {
            'name': 'Teste Fatura Empresa',
            'partner_id': partner.id,
            'journal_id': self.journalrec.id,
            'account_id': self.receivable_account.id,
            'invoice_line_ids': invoice_line_data,
            'pre_invoice_date': '2017-07-01',
        }

        self.invoices = self.env['account.invoice'].create(invoice_values)

        # Email do faturamento
        self.mails = self.env['res.partner.email'].create({
            'email': 'clientefaturamento@mail.com',
            'mail_type': 'invoice',
        })

        # Email do tipo faturamento/cobranca
        self.mails |= self.env['res.partner.email'].create({
            'email': 'clientefaturamentoboleto@mail.com',
            'mail_type': 'invoice-billet',
        })

        # Email do tipo cobranca
        self.mails |= self.env['res.partner.email'].create({
            'email': 'boleto1@mail.com',
            'mail_type': 'billet',
        })

    def test_get_average_margin_percentage(self):

        for invoice in self.invoices:
            invoice._get_average_margin_percentage()
            
            self.assertEqual(invoice.margin_amount, '250.0')
            self.assertEqual(invoice.margin_percentage, '100%')
