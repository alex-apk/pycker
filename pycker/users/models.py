from customfields.models import HasCustomFieldsMixin, CustomFieldsComp
from django.contrib.auth.models import AbstractUser


class User(AbstractUser, HasCustomFieldsMixin):
    is_catalog = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customfield = CustomFieldsComp(self, 1)
