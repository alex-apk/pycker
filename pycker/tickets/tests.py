from django.contrib.auth import get_user_model
from django.conf import settings
from tickets import models as t_models
from lifecycles.models import Lifecycle
from django.test import TestCase


User = get_user_model()


class TestTicketsBasic(TestCase):
    def setUp(self):
        default_lifecycle = settings.DEFAULT_TICKET_LIFECYCLE
        self.lifecycle = Lifecycle.objects.create(name="default",
                                                  lifecycle=default_lifecycle)
        self.queue = t_models.Queue.objects.create(name="default_queue",
                                                   lifecycle=self.lifecycle)
        self.ticket = t_models.Ticket.objects.create(queue=self.queue)

    def test_default_subj(self):
        self.assertEqual(self.ticket.subject, "(no subject)")

    def test_no_owner(self):
        self.assertIsNone(self.ticket.owner)

    def test_owner_assignment(self):
        user = User.objects.create_user(username="test_user",
                                        password="password")
        self.ticket.owner = user
        self.ticket.save()
        self.assertEqual(self.ticket.owner, user)

    def test_state_change(self):
        # simple state change
        self.ticket.status = "open"
        self.assertEqual(self.ticket.status, "open")

        # must fail at changing from stalled to closed
        with self.assertRaises(ValueError):
            self.ticket.status = "closed"

        # must fail at changing from closed
        self.ticket.status = "open"
        self.ticket.status = "resolved"
        self.ticket.status = "closed"

        with self.assertRaises(ValueError):
            self.ticket.status = "deleted"

    def test_wrong_state_on_creation(self):
        with self.assertRaises(ValueError):
            t_models.Ticket.objects.create(queue=self.queue,
                                           _status="bad_status")
