from django.db import models
from django.contrib.auth import get_user_model
from customfields.models import CustomFieldsComp, HasCustomFieldsMixin


User = get_user_model()


class Asset(models.Model):
    catalog = models.ForeignKey("assets.Catalog", on_delete=models.CASCADE,
                                null=False)
    created = models.DateTimeField(auto_now=True, null=False)

    owner = models.ForeignKey(User, on_delete=models.SET_NULL,
                              null=True)
    name = models.CharField(max_length=150, default="",
                            null=False)
    description = models.CharField(max_length=150, default="",
                                   null=False)
    _status = models.CharField(max_length=20, default="new",
                               null=False)

    # TODO: вынести логику статусов в миксин
    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_value):
        valid = self.catalog.lifecycle.next_state_is_valid(self.status, new_value)
        if not valid and (new_value != self.status):
            raise ValueError(f"Can not change status from '{self.status}' "
                             f"to '{new_value}' "
                             f"in lifecycle {self.catalog.lifecycle}")
        self._status = new_value

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.catalog_id = self.catalog.id
        self.customfield = CustomFieldsComp(self, self.catalog.id)

    def save(self, *args, **kwargs):
        if self.status not in self.catalog.lifecycle.lifecycle.keys():
            raise ValueError(f"Can not set status '{self.status}' for "
                             f"lifecycle {self.catalog.lifecycle}")
        super().save(*args, **kwargs)


class Catalog(models.Model, HasCustomFieldsMixin):
    cat_obj_type = "Asset"
    name = models.CharField(max_length=20, null=False)
    lifecycle = models.ForeignKey("lifecycles.Lifecycle", null=False,
                                  on_delete=models.CASCADE)
