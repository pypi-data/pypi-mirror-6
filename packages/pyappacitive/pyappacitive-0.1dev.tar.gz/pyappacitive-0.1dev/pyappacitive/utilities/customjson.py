__author__ = 'sathley'
from json import JSONEncoder, dumps, loads
import datetime
import types


def serialize(obj):

    for k in obj.iterkeys():

        if isinstance(obj[k], datetime.time):
            # convert time to hh:mm:ss:ffffff and the add a trailing 0
            obj[k] = obj[k].strftime('%H:%M:%S.%f') + '0'
        if isinstance(obj[k], datetime.date):
            if isinstance(obj[k], datetime.datetime) is False:
                obj[k] = str(obj[k])
            else:
                # convert datetime to iso
                obj[k] = obj[k].strftime('%Y-%m-%dT%H:%M:%S.%f') + '0Z'

    stringified_object = {k: str(v) if not isinstance(v, types.ListType) and not isinstance(v, types.DictionaryType) else v for k, v in
                               obj.iteritems()}

    return dumps(stringified_object)


def deserialize(obj):
    return loads(obj)