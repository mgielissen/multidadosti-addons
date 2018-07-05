from odoo.tests.common import TransactionCase


class TestResUsers(TransactionCase):

    def setUp(self):
        super(TestResUsers, self).setUp()

    def test_create_user(self):
        user = self.env['res.users'].create({
            'name': 'test user',
            'login': 'test2',
            'groups_id': [4, self.ref('base.group_user')],
        })

        self.assertEqual(user.partner_id.company_id,
                         user.company_id)
        self.assertFalse(user.partner_id.customer)
        self.assertEqual(user.partner_id.parent_id,
                         user.company_id.partner_id)
        self.assertFalse(user.partner_id.supplier)
        self.assertFalse(user.partner_id.is_company)
        self.assertEqual(user.partner_id.company_type, 'person')
