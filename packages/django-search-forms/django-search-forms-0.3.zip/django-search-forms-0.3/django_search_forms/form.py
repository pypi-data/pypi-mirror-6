# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import operator
from django import forms
from django.db.models import Q

from django_search_forms.fields import TextSearchField


class SearchFormMeta(type(forms.Form)):
    """Metaclass for search form."""

    def __new__(mcls, clsname, bases, dict_):
        if 'Meta' in dict_:
            fields = mcls._setup_fields(dict_['Meta'])
            dict_, prev = fields, dict_
            dict_.update(prev)
            for k, v in dict_.items():
                if isinstance(v, forms.Field):
                    v.name = k
        return super(SearchFormMeta, mcls).__new__(mcls, clsname, bases, dict_)

    @classmethod
    def _setup_fields(mcls, opts):
        if hasattr(opts, 'fields'):
            fields = (
                opts.Model._meta.get_field(name)
                for name in opts.fields
            )
        else:
            fields = opts.Model._meta.fields
        return {
            field.name: mcls._get_search_field(field)
            for field in fields
        }

    @classmethod
    def _get_search_field(mcls, field):
        field = TextSearchField()
        return field


class SearchForm(forms.Form):
    """Generic search form for any model."""

    __metaclass__ = SearchFormMeta

    def get_query(self):
        """Get a Q object basing on the form data."""
        self.is_valid()  # Cannot be invalid, so just run the validator
        result = reduce(operator.and_, self.cleaned_data.values(), Q())
        return result
