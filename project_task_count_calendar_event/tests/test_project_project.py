from odoo.tests.common import TransactionCase


class TestProjectProject(TransactionCase):

    def setUp(self):
        super(TestProjectProject, self).setUp()

        # Estagios para teste
        task_type_1 = self.env.ref('project.project_stage_0')
        task_type_2 = self.env.ref('project.project_stage_1')

        # Evento de calendario para teste
        self.ce_1 = self.env.ref('calendar.calendar_event_1')
        self.ce_2 = self.env.ref('calendar.calendar_event_2')

        # Realizamos um union das tarefas e outro
        # dos estagios das tarefas
        task_types = task_type_1 | task_type_2

        self.project = self.env['project.project'].create({
            'name': 'Project teste',
            'privacy_visibility': 'employees',
            'alias_name': 'project+test',
            'partner_id': self.env.ref('base.res_partner_4').id,
            'task_ids': [(6, 0, task_types.ids)]
        })

        self.task_1 = self.env['project.task'].create({
            'name': 'Task 1',
            'user_id': self.env.user.id,
            'project_id': self.project.id,
            'stage_id': task_type_1.id,
        })

        self.task_2 = self.env['project.task'].create({
            'name': 'Task 2',
            'user_id': self.env.user.id,
            'project_id': self.project.id,
            'stage_id': task_type_2.id,
        })

        # Definimos o projeto para o evento de calendario
        self.ce_1.project_id = self.project
        self.ce_2.project_id = self.project

    def test__compute_task_count_fail(self):

        self.task_1.stage_id.state = 'done'
        self.task_2.stage_id.state = 'cancelled'

        self.assertNotEqual(self.task_1.state, 'open')
        self.assertNotEqual(self.task_2.state, 'open')

        self.assertEqual(self.project.task_count, 0)

    def test__compute_task_count_success(self):

        self.task_1.stage_id.state = 'open'
        self.task_2.stage_id.state = 'draft'

        self.assertEqual(self.task_1.state, 'open')
        self.assertEqual(self.task_2.state, 'draft')

        # Somente tarefas com status 'open' sao contabilizadas
        self.assertEqual(self.project.task_count, 2)

    def test__compute_event_number_fail(self):

        self.ce_1.event_state = 'done'
        self.ce_2.event_state = 'cancel'

        self.assertNotEqual(self.ce_1.event_state, 'open')
        self.assertNotEqual(self.ce_2.event_state, 'open')

        self.assertEqual(self.project.event_number, 0)

    def test__compute_event_number_success(self):

        self.ce_1.event_state = 'open'
        self.ce_2.event_state = 'open'

        self.assertEqual(self.ce_1.event_state, 'open')
        self.assertEqual(self.ce_2.event_state, 'open')

        # Somente eventos de calendario com status 'open'
        # sao contabilizados
        self.assertEqual(self.project.event_number, 2)

    def test_action_make_meeting(self):

        res = self.project.action_make_meeting()

        self.assertIsInstance(res, dict)
        self.assertIsInstance(res['context'], dict)

        self.assertEqual(res['id'], self.env.ref(
            'calendar.action_calendar_event').id)
        self.assertEqual(res['name'], 'Meetings')
        self.assertEqual(res['type'], 'ir.actions.act_window')

        ctx = res['context']

        partners = self.env.user.partner_id | self.project.user_id.partner_id

        self.assertEqual(ctx['search_default_partner_ids'], self.env.user.name)
        self.assertEqual(ctx['search_default_project_id'], self.project.id)
        self.assertEqual(ctx['default_customer_partner_id'],
                         self.project.partner_id.id)
        self.assertEqual(ctx['default_partner_ids'], partners.ids)
        self.assertEqual(ctx['default_user_id'], self.env.uid)
        self.assertEqual(ctx['default_name'], self.project.name)
        self.assertEqual(ctx['default_project_id'], self.project.id)
        self.assertEqual(ctx['default_categ_ids'], [
                         self.env.ref('calendar.categ_meet1').id])

    def test_create_calendar_event_from_project(self):

        res = self.project.action_make_meeting()

        # Testamos a criacao de eventos de calendario a partir
        # da tela de projeto. Este teste tem como objetivo
        # verificar se o context fornecido por 'action_make_meeting'
        # realmente esta funcionando, garantindo que os nomes
        # dos campos a serem setados estao corretos
        ce = self.env['calendar.event'].with_context(res['context']).create({
            'start': '2018-09-26 12:00:00',
            'stop': '2018-09-26 14:30:00',
            'description': 'Test Calendar Event',
            'duration': 2.5,
        })

        partners = self.env.user.partner_id | self.project.user_id.partner_id

        self.assertEqual(ce.customer_partner_id, self.project.partner_id)
        self.assertEqual(ce.partner_ids, partners)
        self.assertEqual(ce.user_id.id, self.env.uid)
        self.assertEqual(ce.name, self.project.name)
        self.assertEqual(ce.project_id, self.project)
        self.assertEqual(ce.categ_ids, self.env.ref('calendar.categ_meet1'))
