from django.db import models, IntegrityError
from typing import Union


class CustomField(models.Model):
    name = models.CharField(max_length=40, null=False)
    # TODO: описать возможные типы кастомфилдов как варианты для поля type
    type = models.CharField(max_length=15, null=False)
    multiple = models.BooleanField(null=False, default=False)


class ObjCustomFieldValues(models.Model):
    customfield = models.ForeignKey("customfields.CustomField", null=False,
                                    on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=False)
    object_type = models.CharField(max_length=10, null=False)
    value = models.TextField(null=True, default="")


class CustomFieldToCatalog(models.Model):
    class Meta:
        # each customfield can be assigned to certain catalog only once
        unique_together = ("customfield_id", "catalog_id", "object_type")

    customfield = models.ForeignKey("customfields.CustomField", null=False,
                                    on_delete=models.CASCADE)
    catalog_id = models.PositiveIntegerField(null=False)
    object_type = models.CharField(max_length=10, null=False)


class CustomFieldsComp:
    def __init__(self, parent_instance, cat_id):
        self.parent = parent_instance
        self.parent_obj_type = parent_instance.__class__.__name__
        self.parent_id = self.parent.id
        self.catalog_id = cat_id

    def all(self):
        # TODO: возвращать все кастомфилды объекта (возможно сразу
        # TODO: со значениями?)
        pass

    def add_value(self, field, value):
        customfield = self.__get_customfield(field)
        if not customfield.multiple:
            # TODO: А надо ли кидать эксепшн во всех случаях? Может
            # TODO: быть нужно это делать только если у кастомфилда уже
            # TODO: задано какое-то значение?
            raise ValueError(f"Customfield {customfield} does not allow "
                             f"multiple values")

        ObjCustomFieldValues. \
            objects. \
            create(customfield=customfield,
                   object_id=self.parent.id,
                   object_type=self.parent_obj_type,
                   value=value)

    def remove_value(self, field, value):
        customfield = self.__get_customfield(field)
        qs = self.__get_cf_vals_objs_qs(customfield)
        val = qs.filter(value=value)
        val.delete()

    def __get_customfield(self, item):
        if isinstance(item, int):
            cfs = CustomFieldToCatalog. \
                  objects. \
                  filter(customfield_id=item,
                         catalog_id=self.catalog_id,
                         object_type=self.parent_obj_type).all()
        elif isinstance(item, str):
            cfs = CustomFieldToCatalog.\
                  objects.\
                  filter(customfield__name=item,
                         catalog_id=self.catalog_id,
                         object_type=self.parent_obj_type).all()
        else:
            raise ValueError("Can only get CustomFields by id or by name")
        if cfs:
            cf = cfs.first().customfield
            return cf
        else:
            raise ValueError(f"There is no CustomField with name '{item}' "
                             f"for '{self.parent_obj_type}' in catalog "
                             f"{self.catalog_id}")

    def __get_cf_vals_objs_qs(self, customfield):
        vals = ObjCustomFieldValues. \
            objects. \
            filter(customfield=customfield,
                   object_id=self.parent.id,
                   object_type=self.parent_obj_type)
        return vals

    def __getitem__(self, item):
        customfield = self.__get_customfield(item)
        vals = self.__get_cf_vals_objs_qs(customfield)
        if customfield.multiple:
            return [val.value for val in vals.all()]
        if vals.first():
            return vals.first().value
        return None

    def __setitem__(self, key, value):
        customfield = self.__get_customfield(key)
        qs = self.__get_cf_vals_objs_qs(customfield)
        qs.delete()
        if value is not None:
            if customfield.multiple:
                if isinstance(value, list) or isinstance(value, tuple):
                    for v in value:
                        ObjCustomFieldValues.\
                            objects.\
                            create(customfield=customfield,
                                   object_id=self.parent.id,
                                   object_type=self.parent_obj_type,
                                   value=v)
                    return
            ObjCustomFieldValues. \
                objects. \
                create(customfield=customfield,
                       object_id=self.parent.id,
                       object_type=self.parent_obj_type,
                       value=value)


class HasCustomFieldsMixin:
    is_catalog = True
    cat_obj_type = None

    @property
    def catalog_id(self):
        if self.is_catalog:
            return self.id
        return 1

    def add_customfield(self, customfield: CustomField):
        if self.is_catalog:
            cat_name = self.cat_obj_type
        else:
            cat_name = self.__class__.__name__
        cat_id = self.catalog_id
        try:
            CustomFieldToCatalog.objects.create(customfield=customfield,
                                                catalog_id=cat_id,
                                                object_type=cat_name)
        except IntegrityError as e:
            # TODO: это здесь как заглушка, потом надо решить, что делать
            # TODO: в случае, когда такой кастомфилд уже существует.
            # TODO: Скорее всего, просто возвращать True или False в
            # TODO: зависимости от того, был ли кастомфилд добавлен.
            print(str(e))

    # TODO: выглядит довольно-таки уродливо, особенно вызов. В идеале,
    # TODO: добавление кастомфилдов должно вызываться для инстанса объекта
    # TODO: для каталогов и для класса для объектов без каталогов. Надо
    # TODO: как-то это переписать.
    @staticmethod
    def add_customfield_static(obj, customfield: CustomField):
        cat_name = obj.__name__
        cat_id = 1
        try:
            CustomFieldToCatalog.objects.create(customfield=customfield,
                                                catalog_id=cat_id,
                                                object_type=cat_name)
        except IntegrityError as e:
            print(str(e))

    def remove_customfield(self, customfield: Union[str, int, CustomField]):
        if isinstance(customfield, str):
            # TODO: Возможно неоптимальная схема запросов, надо потестить
            try:
                customfield = CustomField.objects.get(name__iexact=customfield)
            except CustomField.MultipleObjectsReturned:
                cfs = CustomField.objects.filter(name__iexact=customfield).all()
                for cf in cfs:
                    cftc = CustomFieldToCatalog.\
                        objects.\
                        filter(customfield=cf,
                               catalog_id=self.catalog_id,
                               object_type=self.__class__.__name__).all()
                    if cftc:
                        cf.first().delete()
            return

        if isinstance(customfield, int):
            customfield = CustomField.objects.get(pk=customfield)

        CustomFieldToCatalog.\
            objects.\
            filter(customfield=customfield,
                   catalog_id=self.catalog_id,
                   object_type=self.__class__.__name__).first().delete()
