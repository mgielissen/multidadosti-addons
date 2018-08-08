from unittest import mock

from odoo.exceptions import UserError
from odoo.tools import float_compare
from odoo.addons.helpdesk_phonecall_support.tests.test_helpdesk_phonecall_confirm import TestHelpDeskPhoneCallConfirm  # noqa: 501


class TestHelpDeskPhoneCallConfirmTimesheet(TestHelpDeskPhoneCallConfirm):
    def setUp(self):
        super(TestHelpDeskPhoneCallConfirmTimesheet, self).setUp()

    def test_action_confirm_finish_phonecall(self):
        tag = 'helpdesk_phonecall_support.helpdesk_phonecall_service_tag_01'

        start_date_hour = '2017-09-04 14:49:20'
        finish_date_hour = '2017-09-04 15:20:40'

        values = {
            'partner_id': self.partner.id,
            'contact_partner_id': self.partner_contact.id,
            'project_id': self.project.id,
            'description': 'Teste',
            'phonecall_tag_id': self.env.ref(tag).id,
            'start_date_hour': start_date_hour,
        }

        # Finalmente criamos um atendimento
        phonecall = self.env['helpdesk.phonecall.service'].create(values)

        # Referencia para o wizard
        wizard = self.env['helpdesk.phonecall.confirm'].with_context(
            {'active_ids': [phonecall.id]})

        # Executamos o metodo de finalizar o atendimento. Utilizamos o mock
        # para retornamos a data que queremos para que assim seja mais facil
        # verificar se o calculo de data esta correto
        with mock.patch('odoo.fields.Datetime.now') as dt:
            dt.return_value = finish_date_hour
            wizard.action_confirm_finish_phonecall()

        self.assertTrue(phonecall.finish_date_hour)
        self.assertEqual(phonecall.state, 'done')
        self.assertEqual(phonecall.finish_date_hour, finish_date_hour)

        # Executamos o metodo de finalizar o atendimento, verificamos
        # se ele obedece o conceito que apenas atendimentos em aberto podem
        # ser finalizados
        with self.assertRaises(UserError):
            wizard.action_confirm_finish_phonecall()

        timesheet = self.env['account.analytic.line'].search(
            [('helpdesk_id', '=', phonecall.id)])

        self.assertEqual(phonecall.description, timesheet.name)
        self.assertEqual(phonecall.user_id.id, timesheet.user_id.id)
        self.assertEqual(phonecall.partner_id.id, timesheet.customer_partner_id.id)
        self.assertEqual(phonecall.project_id.id, timesheet.project_id.id)
        self.assertEqual(phonecall.company_id.id, timesheet.company_id.id)
        self.assertEqual(phonecall.start_date_hour[:10], timesheet.date)

        # Verificamos a diferença de datas em segundos e a convertemos para
        # horas, já que o widget 'float_time' do Odoo considera o valor de
        # horas em segundos
        hours_diff_decimal = 1880 / 3600.0

        result = float_compare(timesheet.unit_amount,
                               hours_diff_decimal,
                               precision_digits=12)

        # Verificamos se o resultado da comparacao e zero. No Python o valor
        # e considerado False
        self.assertFalse(result)
