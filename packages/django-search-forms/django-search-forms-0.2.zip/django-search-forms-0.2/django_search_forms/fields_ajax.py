"""The fields that depend on bob-ajax-select"""
try:
    from ajax_select.fields import (
        AutoCompleteSelectField,
    )
except ImportError:
    raise ImportError("You need to install bob-ajax-select package")

from django.db.models import Q


class RelatedAjaxSearchField(AutoCompleteSelectField):
    """A field that enables lookup by related objects."""

    def __init__(self, *args, **kwargs):
        kwargs['required'] = False
        super(RelatedAjaxSearchField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if value:
            return Q(**{self.name + '_id': value})
        else:
            return Q()
