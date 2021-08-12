from django.test import TestCase
from assets.models import Asset, Catalog
from tickets.models import Ticket, Queue
from lifecycles.models import Lifecycle
from links.models import Link

from django.contrib.auth import get_user_model
from django.conf import settings


User = get_user_model()


class TestTicketsBasic(TestCase):
    def setUp(self):
        default_t_lifecycle = settings.DEFAULT_TICKET_LIFECYCLE
        self.t_lifecycle = Lifecycle.objects.create(name="default",
                                                  lifecycle=default_t_lifecycle)
        self.queue = Queue.objects.create(name="default_queue",
                                          lifecycle=self.t_lifecycle)
        self.ticket_1 = Ticket.objects.create(queue=self.queue, subject="One")
        self.ticket_2 = Ticket.objects.create(queue=self.queue, subject="Two")

        default_a_lifecycle = settings.DEFAULT_ASSET_LIFECYCLE

        self.a_lifecycle = Lifecycle.objects.create(name="default",
                                                    lifecycle=default_a_lifecycle)
        self.catalog = Catalog.objects.create(name="default_catalog",
                                              lifecycle=self.a_lifecycle)
        self.asset = Asset.objects.create(catalog=self.catalog)

    def test_link_ticket_to_ticket(self):
        self.ticket_1.link(self.ticket_2, "RefersTo")
        link = Link.objects.all().first()

        self.assertEqual(link.source_id, self.ticket_1.id)
        self.assertEqual(link.source_obj_type, "Ticket")
        self.assertEqual(link.link_type, "RefersTo")
        self.assertEqual(link.target_id, self.ticket_2.id)
        self.assertEqual(link.target_obj_type, "Ticket")

    def test_link_ticket_to_asset(self):
        self.ticket_1.link(self.asset, "DependsOn")
        link = Link.objects.all().first()

        self.assertEqual(link.source_id, self.ticket_1.id)
        self.assertEqual(link.source_obj_type, "Ticket")
        self.assertEqual(link.link_type, "DependsOn")
        self.assertEqual(link.target_id, self.asset.id)
        self.assertEqual(link.target_obj_type, "Asset")

    def test_unlinking(self):
        # first we create a link...
        self.ticket_1.link(self.asset, "DependsOn")
        # check that link has been created
        all_links = Link.objects.all()
        self.assertEqual(len(all_links), 1)

        # then we destroy it
        self.ticket_1.unlink(self.asset, "DependsOn")
        # check that link has been destroyed
        all_links = Link.objects.all()
        self.assertEqual(len(all_links), 0)
