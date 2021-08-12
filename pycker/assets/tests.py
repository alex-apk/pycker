from django.contrib.auth import get_user_model
from django.conf import settings
from assets import models as a_models
from lifecycles.models import Lifecycle
from django.test import TestCase


User = get_user_model()


class TestAssetsBasic(TestCase):
    def setUp(self):
        default_lifecycle = settings.DEFAULT_ASSET_LIFECYCLE
        self.lifecycle = Lifecycle.objects.create(name="default",
                                                  lifecycle=default_lifecycle)
        self.catalog = a_models.Catalog.objects.create(name="default_catalog",
                                                       lifecycle=self.lifecycle)
        self.asset = a_models.Asset.objects.create(catalog=self.catalog)

    def test_default_name(self):
        self.assertEqual(self.asset.name, "")

    def test_no_owner(self):
        self.assertIsNone(self.asset.owner)

    def test_owner_assignment(self):
        user = User.objects.create_user(username="test_user",
                                        password="password")
        self.asset.owner = user
        self.asset.save()
        self.assertEqual(self.asset.owner, user)

    def test_state_change(self):
        # simple state change
        self.asset.status = "allocated"
        self.assertEqual(self.asset.status, "allocated")

        # must fail at changing from allocated to new
        with self.assertRaises(ValueError):
            self.asset.status = "new"

    def test_wrong_state_on_creation(self):
        with self.assertRaises(ValueError):
            a_models.Asset.objects.create(catalog=self.catalog,
                                          _status="bad_status")
