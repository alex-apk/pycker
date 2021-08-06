from django.db import models
from django.contrib.auth import get_user_model
from customfields.models import CustomFieldsComp, HasCustomFieldsMixin


User = get_user_model()


class Ticket(models.Model):
    queue = models.ForeignKey("tickets.Queue", on_delete=models.CASCADE,
                              null=False)
    created = models.DateTimeField(auto_now=True, null=False)

    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              null=True)
    subject = models.CharField(max_length=150, default="(no subject)",
                               null=False)
    _status = models.CharField(max_length=20, default="new",
                               null=False)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_value):
        valid = self.queue.lifecycle.next_state_is_valid(self.status, new_value)
        if not valid and (new_value != self.status):
            raise ValueError(f"Can not change status from '{self.status}' "
                             f"to '{new_value}' "
                             f"in lifecycle {self.queue.lifecycle}")
        self._status = new_value

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.catalog_id = self.queue.id
        self.customfield = CustomFieldsComp(self, self.queue.id)

    def save(self, *args, **kwargs):
        if self.status not in self.queue.lifecycle.lifecycle.keys():
            raise ValueError(f"Can not set status '{self.status}' for "
                             f"lifecycle {self.queue.lifecycle}")
        super().save(*args, **kwargs)


class Queue(models.Model, HasCustomFieldsMixin):
    cat_obj_type = "Ticket"
    name = models.CharField(max_length=20, null=False)
    lifecycle = models.ForeignKey("lifecycles.Lifecycle", null=False,
                                  on_delete=models.CASCADE)
