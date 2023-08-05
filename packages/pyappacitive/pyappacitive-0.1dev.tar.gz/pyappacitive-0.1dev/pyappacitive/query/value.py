from datetime import date, datetime
import types

__author__ = 'sathley'


class ValueBase(object):
    def __init__(self):
        self.value = None

    def __repr__(self):
        raise NotImplementedError('This method should be overridden in derived classes.')


class StringValue(ValueBase):

    def __init__(self, value):
        super(StringValue, self).__init__()
        self.value = value

    def __repr__(self):
        if isinstance(self.value, str) is False:
            raise TypeError(self.value + 'is not a valid string value.')
        return "'{0}'".format(self.value)


class IntegerValue(ValueBase):

    def __init__(self, value):
        super(IntegerValue, self).__init__()
        self.value = value

    def __repr__(self):
        if isinstance(self.value, int) is False:
            raise TypeError(self.value + 'is not a valid integer value.')
        return str(self.value)


class DecimalValue(ValueBase):

    def __init__(self, value):
        super(DecimalValue, self).__init__()
        self.value = value

    def __repr__(self):
        if isinstance(self.value, float) is False:
            raise TypeError(self.value + 'is not a valid decimal value.')
        return str(self.value)


class DateValue(ValueBase):

    def __init__(self, value):
        super(DateValue, self).__init__()
        self.value = value

    def __repr__(self):
        if isinstance(self.value, date) is False:
            raise TypeError(self.value + 'is not a valid date value.')
        return "date('{0}')".format(str(self.value))


class DatetimeValue(ValueBase):

    def __init__(self, value):
        super(DatetimeValue, self).__init__()
        self.value = value

    def __repr__(self):
        if isinstance(self.value, date) is False and isinstance(self.value, datetime) is False:
            raise TypeError(self.value + 'is not a valid datetime value.')
        return "datetime('{0}')".format(str(self.value))


class BooleanValue(ValueBase):

    def __init__(self, value):
        super(BooleanValue, self).__init__()
        self.value = value

    def __repr__(self):
        if isinstance(self.value, bool) is False:
            raise TypeError(self.value + 'is not a valid boolean value.')
        return str(self.value)


class GeoValue(ValueBase):

    def __init__(self, latitude, longitude):
        super(GeoValue, self).__init__()
        self.value = latitude, longitude

    def __repr__(self):
        latitude, longitude = self.value
        if isinstance(latitude, types.FloatType) is False or isinstance(longitude, types.FloatType) is False:
            raise TypeError('Latitude : {0} and Longitude : {1} value is invalid.'.format(latitude, longitude))
        return "{0},{1}".format(latitude, longitude)


class DistanceValue(ValueBase):

    def __init__(self, distance, metric):
        super(DistanceValue, self).__init__()
        self.value = distance, metric
        self.valid_metrics = ['mi', 'km']

    def __repr__(self):
        distance, metric = self.value
        if isinstance(distance, (types.IntType, types.LongType, types.FloatType)) is False:
            raise TypeError('"{0}" is an invalid value for distance.'.format(distance))
        if isinstance(metric, str) is False or metric.lower() not in self.valid_metrics:
            raise TypeError('"{0}" is an invalid metric for distance. Valid values are "km" or "mi".'.format(metric))

        return '{0} {1}'.format(str(distance), metric)


class GeoValues(ValueBase):

    def __init__(self, geo_values):
        super(GeoValues, self).__init__()
        self.value = geo_values

    def __repr__(self):
        if isinstance(self.value, types.ListType) is False:
            raise TypeError('GeoValues should be list of GeoValue.')
        return ' | '.join(str(geo) for geo in self.value)
