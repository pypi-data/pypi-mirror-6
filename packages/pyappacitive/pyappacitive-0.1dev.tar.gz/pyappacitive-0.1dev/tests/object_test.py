from pyappacitive import AppacitiveObject, AppacitiveConnection, ValidationError, AppacitiveError
from pyappacitive.utilities import logfilter
import datetime
from nose.tools import *
import logging


def create_object_test():
    #logger = logging.getLogger('pyappacitive')
    #
    #logger.setLevel(logging.DEBUG)
    #sh = logging.StreamHandler()
    #sh.addFilter(logfilter.FailedRequestsLogFilter())
    #logger.addHandler(sh)
    obj = AppacitiveObject('object')
    obj.set_property('intfield', 100)
    obj.set_property('decimalfield', 20.250)
    obj.set_property('boolfield', True)
    obj.set_property('stringfield', 'hello world')
    obj.set_property('textfield', '''Objects represent your data stored inside the Appacitive platform. Every object is mapped to the type that you create via the designer in your management console. If we were to use conventional databases as a metaphor, then a type would correspond to a table and an object would correspond to one row inside that table.

The object api allows you to store, retrieve and manage all the data that you store inside Appacitive. You can retrieve individual records or lists of records based on a specific filter criteria.''')
    obj.set_property('datefield', datetime.date.today())
    obj.set_property('timefield', datetime.time.min)
    obj.set_property('datetimefield', datetime.datetime(2005,5,5,5))
    obj.set_property('geofield', '10.10,20.20')
    obj.set_property('multifield', ['val1', 500, False])

    obj.create()
    assert obj.id > 0


def get_object_test():
    obj = AppacitiveObject('object')
    obj.create()

    resp = AppacitiveObject.get('object', obj.id)
    assert hasattr(resp, 'object')
    assert resp.object is not None
    assert resp.object.id == obj.id


def multiget_object_test():
    object_ids = []
    for i in range(12):
        obj = AppacitiveObject('object')
        obj.create()
        object_ids.append(obj.id)

    resp = AppacitiveObject.multi_get('object', object_ids)
    assert hasattr(resp, 'objects')
    assert len(resp.objects) == 12


def delete_object_test():
    obj = AppacitiveObject('object')
    obj.create()
    id = obj.id
    obj.delete()
    try:
        resp = AppacitiveObject.get('object', id)
    except AppacitiveError as e:
        assert e.code == '404'

@raises(AppacitiveError)
def delete_object_with_connection_test():
    conn = AppacitiveConnection('sibling').from_new_object('object', AppacitiveObject('object')).to_new_object('object', AppacitiveObject('object'))
    conn.create()
    conn_id = conn.id
    obj = conn.endpoint_a.object
    obj.delete_with_connections()
    try:
        response = AppacitiveConnection.get('sibling', conn_id)
    except AppacitiveError as e:
        assert e.code != '200'
        raise e


def multi_delete_object_test():
    object_ids = []
    for i in range(10):
        obj = AppacitiveObject('object')
        obj.create()
        object_ids.append(obj.id)

    AppacitiveObject.multi_delete('object', object_ids)

    for object_id in object_ids:
        try:
            resp = AppacitiveObject.get('object', object_id)
        except AppacitiveError as e:
            assert e.code == '404'


def update_object_test():
    obj = AppacitiveObject('object')
    obj.set_property('intfield', 100)
    obj.set_property('decimalfield', 10.10)
    obj.set_property('boolfield', False)
    obj.set_property('stringfield', 'hello world')
    obj.set_property('textfield', '''Objects represent your data stored inside the Appacitive platform. Every object is
    mapped to the type that you create via the designer in your management console. If we were to use conventional
    databases as a metaphor, then a type would correspond to a table and an object would correspond to one
    row inside that table.


                        The object api allows you to store, retrieve and manage all the data that you store inside
                        Appacitive. You can retrieve individual records or lists of records based on a specific filter
                        criteria.''')
    obj.set_property('datefield', datetime.date.today())
    obj.set_property('timefield', datetime.time.min)
    obj.set_property('datetimefield', datetime.datetime.now())
    obj.set_property('geofield', '10.10,20.20')
    obj.set_property('multifield', ['val1', 'val2', 'val3'])

    obj.create()

    obj.set_property('intfield', 200)
    obj.set_property('decimalfield', 20.20)
    obj.set_property('boolfield', True)
    obj.set_property('stringfield', 'world hello')
    obj.set_property('textfield', '''To update an existing object, you need to provide the type
    and id of the object along with the list
    of updates that are to be made. As the Appacitive platform supports
    partial updates, and update only needs the information that has
    actually changed.''')
    obj.set_property('datefield', datetime.date(1990, 5, 20))
    obj.set_property('timefield', datetime.time.max)
    obj.set_property('datetimefield', datetime.datetime(2000, 2, 3))
    obj.set_property('geofield', '30.30, 40.40')
    obj.set_property('multifield', ['val4', 'val5', 'val6'])

    obj.update()
    assert obj.get_property('intfield') == str(200)
    assert obj.get_property('boolfield') == str(True)


def find_object_between_two_objects_test():
    conn = AppacitiveConnection('sibling').from_new_object('object', AppacitiveObject('object')).to_new_object('object', AppacitiveObject('object'))
    conn.create()

    conn1 = AppacitiveConnection('sibling').from_existing_object_id('object', conn.endpoint_a.objectid).to_new_object('object', AppacitiveObject('object'))
    conn1.create()

    response = AppacitiveObject.find_in_between_two_objects('object', conn.endpoint_b.objectid, 'sibling', 'object', conn1.endpoint_b.objectid, 'sibling', 'object')
    assert hasattr(response, 'objects')
    assert len(response.objects) == 1


@raises(ValidationError)
def create_object_without_type_test():
    obj = AppacitiveObject(None)
    response = obj.create()
    assert response is None

@raises(AppacitiveError)
def create_invalid_object_test():
    obj = AppacitiveObject('non_existent_schema')
    try:
        obj.create()
    except AppacitiveError as e:
        assert e.code == '404'
        raise e