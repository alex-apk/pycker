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
            CustomField.objects.create(name="cf3", type="type3", multiple=True),
            CustomField.objects.create(name="cf4", type="type4", multiple=True)
        ]

        for cf in self.customfields:
            self.queue.add_customfield(cf)

    def test_set_cf_value(self):
        test_value = "test value"
        ticket = Ticket.objects.create(queue=self.queue)
        ticket.customfield["cf1"] = test_value
        self.assertEqual(ticket.customfield["cf1"], test_value)
        self.assertIsNone(ticket.customfield["cf2"])

    def test_add_remove_cf_value(self):
        ticket = Ticket.objects.create(queue=self.queue)
        # add to multiple
        ticket.customfield.add_value("cf3", "val1")
        # multiple type customfields should always return lists
        self.assertEqual(ticket.customfield["cf3"], ["val1"])
        ticket.customfield.add_value("cf3", "val2")
        ticket.customfield.add_value("cf3", "val3")
        self.assertEqual(ticket.customfield["cf3"], ["val1", "val2", "val3"])

        # test adding multiple type customfield value to a list
        test_cf4_vals = ["1", "2", "3"]
        ticket.customfield.add_value("cf4", test_cf4_vals)
        self.assertEqual(ticket.customfield["cf4"], test_cf4_vals)

        for v in test_cf4_vals:
            ticket.customfield.remove_value("cf4", v)

        # test setting multiple type customfield value to a list
        ticket.customfield["cf4"] = test_cf4_vals
        self.assertEqual(ticket.customfield["cf4"], test_cf4_vals)

        # remove one value
        ticket.customfield.remove_value("cf3", "val1")
        # should have two values left in that customfield now
        self.assertEqual(ticket.customfield["cf3"], ["val2", "val3"])

        # should not modify cf values
        ticket.customfield.remove_value("cf3", "val1")
        self.assertEqual(ticket.customfield["cf3"], ["val2", "val3"])

        # cf1 is not multiple, should raise ValueError as of now
        with self.assertRaises(ValueError):
            ticket.customfield.add_value("cf1", "bad value")

        ticket.customfield["cf1"] = "good value"
        self.assertEqual(ticket.customfield["cf1"], "good value")

        # removing values should work regardless of customfield type
        ticket.customfield.remove_value("cf1", "good value")
        self.assertIsNone(ticket.customfield["cf1"])

    def test_add_cf_to_users(self):
        user = User.objects.create_user(username="test", password="password")
        test_value = "test value 2"
        User.add_customfield_static(User, self.customfields[0])

        user.customfield["cf1"] = test_value
        self.assertEqual(user.customfield[1], test_value)
