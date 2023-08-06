import re
from collections import namedtuple

from django import forms
from django.db.models import Q

from ralph import ui


QUOTATION_MARKS = re.compile(r'^"(.+)"$')


Search = namedtuple('Search', ['is_exact', 'string'])


class DateRangeWidget(forms.MultiWidget):
    """A widget for date range search."""

    def __init__(self, *args, **kwargs):
        kwargs['widgets'] = [
            ui.widgets.DateWidget(),
            ui.widgets.DateWidget(),
        ]
        super(DateRangeWidget, self).__init__(*args, **kwargs)


class DateRangeSearchField(forms.MultiValueField):
    """A field that represents a search for a range of dates."""

    def __init__(self, *args, **kwargs):
        kwargs['required'] = False
        kwargs['widget'] = DateRangeWidget()
        kwargs['fields'] = [
            forms.DateField(),
            forms.DateField(),
        ]
        super(DateRangeSearchField, self).__init__(*args, **kwargs)

    def compress(self, values):
        result = Q()
        for suffix, value in zip(['gte', 'lte'], values):
            if value is not None:
                result &= Q(**{self.name + '__' + suffix: value})
        return result


class SearchField(forms.Field):
    """The generic search field."""

    def __init__(self, *args, **kwargs):
        kwargs['required'] = False
        super(SearchField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(SearchField, self).clean(value)
        if not value:
            return Q()
        return self.get_query(value)


class ExactSearchField(SearchField, forms.CharField):
    """The field always searches exactly"""

    def get_query(self, value):
        return Q(**{self.name: value})


UNQUOTED_VALUE = (r'(?P<content_uq>[^",]+)(,|$)')
QUOTED_VALUE = (r'"(?P<content_q>(""|[^"])+)"(,|$)')
SINGLE_VALUE = re.compile('|'.join([UNQUOTED_VALUE, QUOTED_VALUE]))


class MultiSearchField(SearchField, forms.CharField):
    """The field that allows one to specify several comma-separated values."""

    def get_query(self, value):
        values = [
            (
                match.group('content_uq') or
                match.group('content_q')
            ).strip().replace('""', '"')
            for match in SINGLE_VALUE.finditer(value)
        ]
        return Q(**{self.name + '__in': values})



class RelatedSearchField(SearchField, forms.ChoiceField):
    """A field that allows to search from a limited set of related objects.
    You need ajax if you want to search a big sets."""

    def __init__(self, Model, *args, **kwargs):
        self.Model = Model
        kwargs['choices'] = [('', '----')] + [
            (unicode(object_.id), unicode(object_))
            for object_ in self.Model.objects.all()
        ]
        super(RelatedSearchField, self).__init__(*args, **kwargs)

    def get_query(self, value):
        return Q(**{self.name + '__id': int(value)})


class TextSearchField(SearchField, forms.CharField):
    """The field that allows using quotes for exact searches"""

    def __init__(self, *args, **kwargs):
        kwargs['required'] = False
        super(TextSearchField, self).__init__(*args, **kwargs)

    def _parse_search(self, value):
        """Parses the search string."""
        match = QUOTATION_MARKS.match(value)
        if match is None:
            return Search(is_exact=False, string=value)
        else:
            return Search(is_exact=True, string=match.group(1))

    def get_query(self, value):
        search = self._parse_search(value)
        if search.is_exact:
            return Q(**{self.name: search.string})
        else:
            return Q(**{self.name + '__icontains': search.string})
