# -*- coding: utf-8 -*-

from odoo.addons.br_account.tests.test_account_invoice import (
    TestAccountInvoice)


class TestAccountUtils(TestAccountInvoice):
    def setUp(self):
        super(TestAccountUtils, self).setUp()

    def test_action_invoice_cancel_paid_with_backup(self):
        for inv in self.invoices:

            inv.action_br_account_invoice_open()
            move_dict = inv._prepare_dict_to_create_backup_record(inv.move_id)
            inv.action_invoice_cancel_paid()
            backup_line = self.env['account.move.backup.line'].search([
                ('invoice_id', '=', inv.id)])[0]
            backup_move = backup_line.move_id

            # FIX
            # self.assertEqual(
            #     move_dict,
            #     inv._prepare_dict_to_create_backup_record(backup_move))
