from django.contrib.auth import get_user_model
from tickets.models import Queue
from assets.models import Catalog
from lifecycles.models import Lifecycle
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError




class Command(BaseCommand):
    help = 'Initializes the DB with some general basic data'

    def handle(self, *args, **options):
        User = get_user_model()

        asset_lifecycle = settings.DEFAULT_ASSET_LIFECYCLE
        ticket_lifecycle = settings.DEFAULT_TICKET_LIFECYCLE
        self.stdout.write("Creating lifecycles")
        asset_lifecycle = Lifecycle.objects.create(name="asset_default",
                                                   lifecycle=asset_lifecycle)
        ticket_lifecycle = Lifecycle.objects.create(name="ticket_default",
                                                    lifecycle=ticket_lifecycle)

        self.stdout.write("Creating queue")
        Queue.objects.create(id=1, name="default", lifecycle=ticket_lifecycle)

        self.stdout.write("Creating catalog")
        Catalog.objects.create(id=1, name="default", lifecycle=asset_lifecycle)

        self.stdout.write("Creating admin user")
        User.objects.create_user(id=1, username="admin", password="trackeradmin")

        self.stdout.write("All done")
