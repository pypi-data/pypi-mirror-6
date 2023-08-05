__author__ = 'sathley'

import types
import datetime
from pyappacitive import ValidationError


class FilterBase(object):
    def __init__(self):
        self.operator = None
        self.key = None
        self.value = None

    def __repr__(self):
        raise NotImplementedError('This method should be overridden in derived classes.')


class PropertyFilter(FilterBase):
    def __init__(self, property_name):
        super(PropertyFilter, self).__init__()
        self.key = property_name

    def __repr__(self):

        #   Handle date,time and datetime datatypes
        if isinstance(self.value, datetime.time):
            self.value = "time('{0}')".format(str(self.value))

        if isinstance(self.value, datetime.date):
            if isinstance(self.value, datetime.datetime) is False:
                self.value = "date('{0}')".format(str(self.value))
            else:
                self.value = "datetime('{0}')".format(str(self.value))

        if self.operator == 'between':
            value1, value2 = self.value
            return "*{0} {1} ({2},{3})".format(self.key, self.operator, str(value1), str(value2))

        if isinstance(self.value, str):
            return "*{0} {1} '{2}'".format(self.key, self.operator, str(self.value))

        return "*{0} {1} {2}".format(self.key, self.operator, str(self.value))

    def is_equal_to(self, value):
        self.value = value
        self.operator = '=='
        return self

    def is_not_equal_to(self, value):

        self.value = value
        self.operator = '!='
        return self

    def is_greater_than(self, value):

        self.value = value
        self.operator = '>'
        return self

    def is_less_than(self, value):

        self.value = value
        self.operator = '<'
        return self

    def is_greater_than_equal_to(self, value):

        self.value = value
        self.operator = '>='
        return self

    def is_less_than_equal_to(self, value):

        self.value = value
        self.operator = '<='
        return self

    def like(self, value):

        self.value = value
        self.operator = 'like'
        return self

    def starts_with(self, value):

        self.value = value+'*'
        self.operator = 'like'
        return self

    def ends_with(self, value):

        self.value = '*'+value
        self.operator = 'like'
        return self

    def between(self, start, end):
        self.value = (start, end)
        self.operator = 'between'
        return self


class GeoFilter(FilterBase):
    def __init__(self, property_name):
        super(GeoFilter, self).__init__()
        self.key = property_name

    def __repr__(self):

        if self.operator == 'within_circle':
            geo_code, distance = self.value
            return "*{0} {1} {2},{3}".format(self.key, self.operator, str(geo_code), str(distance))

        elif self.operator == 'within_polygon':
            geo_codes = self.value
            return "*{0} {1} {2}".format(self.key, self.operator, ' | '.join(geo_codes))

        else:
            raise ValidationError('Incorrect geo filter')

    def within_circle(self, geo_code, distance):
        self.operator = 'within_circle'
        self.value = (geo_code, distance)
        return self

    def within_polygon(self, geo_codes):
        self.operator = 'within_polygon'
        self.value = geo_codes
        return self


class AttributeFilter(FilterBase):
    def __init__(self, attribute_key):
        super(AttributeFilter, self).__init__()
        self.key = attribute_key

    def __repr__(self):
        return "@{0} {1} '{2}'".format(self.key, self.operator, str(self.value))

    def is_equal_to(self, value):
        self.operator = '=='
        self.value = value
        return self

    def like(self, value):
        self.operator = 'like'
        self.value = value
        return self

    def starts_with(self, value):
        self.operator = 'like'
        self.value = value+'*'
        return self

    def ends_with(self, value):
        self.operator = 'like'
        self.value = '*'+value
        return self


class AggregateFilter(FilterBase):
    def __init__(self, property_name):
        super(AggregateFilter, self).__init__()
        self.key = property_name

    def __repr__(self):
        return "${0} {1} {2}".format(self.key, self.operator, str(self.value))

    def is_equal_to(self, value):
        self.operator = '=='
        self.value = value
        return self

    def is_not_equal_to(self, value):
        self.operator = '!='
        self.value = value
        return self

    def is_greater_than(self, value):
        self.operator = '>'
        self.value = value
        return self

    def is_less_than(self, value):
        self.operator = '<'
        self.value = value
        return self

    def is_greater_than_equal_to(self, value):
        self.operator = '>='
        self.value = value
        return self

    def is_less_than_equal_to(self, value):
        self.operator = '<='
        self.value = value
        return self


class TagFilter(FilterBase):

    def __init__(self):
        super(TagFilter, self).__init__()
        self.tags = []
        self.operator = None

    def __repr__(self):
        if isinstance(self.tags, types.ListType) is False:
            raise TypeError('Expected list of string tags.')
        return "{0}('{1}')".format(self.operator, ','.join(self.tags))

    def match_one_or_more(self, tags):
        self.tags = tags
        self.operator = 'tagged_with_one_or_more'
        return self

    def match_all(self, tags):
        self.tags = tags
        self.operator = 'tagged_with_all'
        return self
