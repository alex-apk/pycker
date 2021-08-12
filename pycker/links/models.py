from django.db import models


class Link(models.Model):
    created = models.DateTimeField(auto_now=True, null=False)
    source_obj_type = models.CharField(max_length=20, null=False, blank=False)
    source_id = models.PositiveIntegerField(null=False)
    link_type = models.CharField(max_length=20, null=False, blank=False)
    target_obj_type = models.CharField(max_length=20, null=False, blank=False)
    target_id = models.PositiveIntegerField(null=False)


class LinkableMixin:
    @property
    def linkable_obj_type(self):
        return self.__class__.__name__

    def __get_existing_link(self, target, link_type):
        if not isinstance(target, LinkableMixin):
            raise TypeError("Target is not linkable")

        link_payload = self.__get_link_payload(target, link_type)

        existing_link = Link.objects.filter(**link_payload).first()
        return existing_link

    def __get_link_payload(self, target, link_type):
        link_payload = {
            "source_id": self.pk,
            "source_obj_type": self.linkable_obj_type,
            "link_type": link_type,
            "target_id": target.pk,
            "target_obj_type": target.linkable_obj_type,
        }
        return link_payload

    def link(self, target, link_type):
        existing_link = self.__get_existing_link(target, link_type)
        if existing_link:
            raise ValueError(f"{self.__class__.__name__} #{self.pk} already "
                             f"has link '{link_type}' to "
                             f"{target.__class__.__name__} #{target.pk}")

        link_payload = self.__get_link_payload(target, link_type)

        Link.objects.create(**link_payload)

    def unlink(self, target, link_type):
        existing_link = self.__get_existing_link(target, link_type)
        if existing_link:
            existing_link.delete()
