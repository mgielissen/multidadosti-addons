import datetime, time

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestCalendarEventPartner(TransactionCase):

    def setUp(self):
        super(TestCalendarEventPartner, self).setUp()

        main_company = self.env.ref('base.main_company')

        test_user_01 = self.env['res.users'].create({
            'name': 'Test user 1',
            'login': 'user1@example.com',
            'new_password': 'user1',
        })

        test_user_02 = self.env['res.users'].create({
            'name': 'Test user 2',
            'login': 'user2@example.com',
            'new_password': 'user2',
        })

        self.users = test_user_01 | test_user_02

        # Os dois partners pertencentes ao usuario de teste
        # pretencem a mesma empresa
        test_user_01.partner_id.parent_id = main_company.partner_id
        test_user_02.partner_id.parent_id = main_company.partner_id

        # Parceiro de teste que não pertence a empresa main_company
        test_partner = self.env['res.partner'].create({'name': 'Partner Test'})

        # Trocamos o parceiro do calendario para o parceiro
        # do user demo, de modo a facilitar os testes
        # Estes sao os parceiros que participam do evento de calendario
        partners = test_user_01.partner_id | test_user_02.partner_id | test_partner

        project = self.env.ref('project.project_project_1')

        values = {
            'active': True,
            'user_id': test_user_01.id,
            'project_id': project.id,
            'task_id': self.env.ref('project.project_task_2').id,
            'customer_partner_id': project.partner_id.id,
            'company_partner_id': main_company.partner_id.id,
            'partner_ids': [(6, 0, partners.ids)],
            'name': 'Calendar Event Test',
            'description': 'Meeting to discuss project plan and hash out the details of implementation.',
            'start': time.strftime('%Y-%m-03 10:20:00'),
            'categ_ids': [(6, 0, self.env.ref('calendar.categ_meet1').ids)],
            'stop': time.strftime('%Y-%m-03 16:30:00'),
            'duration': 6.3,
            'allday': False,
            'state': 'open',
        }

        self.ce = self.env['calendar.event'].create(values)

        self.wizard = self.env['calendar.event.finish'].create(
            {'calendar_event_id': self.ce.id})

    def test_action_finish_calendar_event_raise_exception(self):

        self.ce.project_id = False

        with self.assertRaises(UserError):
            self.wizard.action_finish_calendar_event()

    def test_action_finish_calendar_event_ok(self):

        # Inicialmente, removes todas as entradas
        # da planilha de dados de modo a facilitar o teste
        self.env['account.analytic.line'].search([]).unlink()

        # Realizamos a finalizacao do evento
        self.wizard.action_finish_calendar_event()

        analytic_lines = self.env['account.analytic.line'].search([])

        # A finalizacao do evento deve criar apenas uma entrada
        # na planilha de horas
        self.assertEqual(len(analytic_lines), 2)

        for line in analytic_lines:

            self.assertEqual(line.name, self.ce.name)
            self.assertEqual(line.date, self.ce.start_datetime[:10])
            self.assertIn(line.user_id.id, self.users.ids)
            self.assertEqual(line.customer_partner_id.id, self.ce.customer_partner_id.id)

            self.assertEqual(line.company_id.id,
                             self.ce.user_id.company_id.id)

            self.assertEqual(line.project_id.id, self.ce.project_id.id)
            self.assertEqual(line.unit_amount, self.ce.event_duration)
            self.assertEqual(line.calendar_event_id.id, self.ce.id)

            self.assertEqual(line.task_id.id, self.ce.task_id.id)
            self.assertEqual(line.project_task_type_id.id,
                             self.ce.task_id.stage_id.id)

    def test__get_account_analyticline_values(self):

        dt = datetime.datetime.strptime(self.ce.start_datetime,
                                       '%Y-%m-%d %H:%M:%S')

        value = self.wizard._get_account_analytic_line_values(
            user=self.ce.user_id, calendar_event=self.ce, start_datetime=dt)

        self.assertIsInstance(value, dict)

        self.assertEqual(value['name'], self.ce.name)
        self.assertEqual(value['date'], dt.date())
        self.assertEqual(value['user_id'], self.ce.user_id.id)
        self.assertEqual(value['customer_partner_id'], self.ce.customer_partner_id.id)

        self.assertEqual(value['company_id'], self.ce.partner_id.company_id.id)

        self.assertEqual(value['project_id'], self.ce.project_id.id)
        self.assertEqual(value['unit_amount'], self.ce.event_duration)
        self.assertEqual(value['calendar_event_id'], self.ce.id)

        self.assertEqual(value['task_id'], self.ce.task_id.id)
        self.assertEqual(value['project_task_type_id'],
                         self.ce.task_id.stage_id.id)
