import unittest

from mail import FakeMailer
from service import Actor, AppointmentService, connect, init_db


class ExistingContract(unittest.TestCase):
    def setUp(self):
        self.database = connect(':memory:')
        self.addCleanup(self.database.close)
        init_db(self.database)
        self.service = AppointmentService(self.database, FakeMailer())
        self.actor = Actor('a', 'requester-a', 'requester')

    def test_create_returns_identity_and_preserves_details(self):
        self.assertEqual('one', self.service.create(self.actor, 'one', '2026-11-01T10:00:00Z'))
        row = self.service.list(self.actor)[0]
        self.assertEqual('requester-a', row['requester_id'])
        self.assertEqual('2026-11-01T10:00:00Z', row['starts_at'])

    def test_list_is_customer_scoped(self):
        self.service.create(self.actor, 'one', '2026-11-01T10:00:00Z')
        self.assertEqual([], self.service.list(Actor('b', 'requester-b', 'requester')))


if __name__ == '__main__':
    unittest.main()
