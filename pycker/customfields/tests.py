from django.test import TestCase
from tickets.models import Queue, Ticket
from lifecycles.models import Lifecycle
from customfields.models import CustomField

from django.conf import settings
from users.models import User


class CFTest(TestCase):
    def setUp(self):
        lifecycle = settings.DEFAULT_TICKET_LIFECYCLE
        self.lifecycle = Lifecycle.objects.create(name="default",
                                                  lifecycle=lifecycle)
        self.queue = Queue.objects.create(name="default",
                                          lifecycle=self.lifecycle)

        # TODO: заменить типы-заглушки на нормальные
        self.customfields = [
            CustomField.objects.create(name="cf1", type="type1"),
            CustomField.objects.create(name="cf2", type="type2"),
            CustomField.objects.create(name="cf3", type="type3"),
            CustomField.objects.create(name="cf4", type="type4")
        ]

    def test_add_cfs_to_queue(self):
        for cf in self.customfields:
            self.queue.add_customfield(cf)

    def test_add_cf_value(self):
        for cf in self.customfields:
            self.queue.add_customfield(cf)

        test_value = "test value"
        ticket = Ticket.objects.create(queue=self.queue)
        ticket.customfield["cf1"] = test_value
        self.assertEqual(ticket.customfield["cf1"], test_value)
        self.assertIsNone(ticket.customfield["cf2"])

    def test_add_cf_to_users(self):
        user = User.objects.create_user(username="test", password="password")
        test_value = "test value 2"
        User.add_customfield_static(User, self.customfields[0])

        user.customfield["cf1"] = test_value
        self.assertEqual(user.customfield[1], test_value)
