__author__ = 'sathley'

from pyappacitive import *
import random


def get_random_number(number_of_digits=10):
    arr = [str(i) for i in range(number_of_digits)]
    random.shuffle(arr)
    return int(''.join(arr))


def search_objects_pnum_psize_test():
    query = AppacitiveQuery()
    query.page_number = 2
    query.page_size = 15

    response = AppacitiveObject.find('object', query)
    assert response.paging_info.page_number == 2
    assert response.paging_info.page_size == 15
    assert hasattr(response, 'objects')


def search_with_freetext_tokens_test():
    obj = AppacitiveObject('object')
    obj.set_property('textfield', '''Karan Arjun is a 1995 Bollywood action thriller film starring Raakhee, Shahrukh Khan, Salman Khan, Amrish Puri, Kajol, Mamta Kulkarni and Ranjeet. The film was directed by Rakesh Roshan and written by Ravi Kapoor and Sachin Bhowmick.''')
    obj.create()
    query = AppacitiveQuery()
    query.free_text_tokens = ['Shahrukh', 'Khan', 'Salman']

    response = AppacitiveObject.find('object', query)
    assert len(response.objects) > 0


def search_with_integer_property_filter_test():
    obj = AppacitiveObject('object')
    random_num = get_random_number()
    obj.set_property('intfield', random_num)
    obj.create()

    query = AppacitiveQuery()
    query.filter = PropertyFilter('intfield').is_equal_to(random_num)

    response = AppacitiveObject.find('object', query)
    assert response.paging_info.total_records == 1
    assert len(response.objects) == 1


def search_with_decimal_property_filter_test():
    obj = AppacitiveObject('object')
    random_num1 = get_random_number(5)
    random_num2 = get_random_number(5)
    random_float = float(str(random_num1)+'.'+str(random_num2))
    obj.set_property('decimalfield', random_float)
    obj.create()

    query = AppacitiveQuery()
    query.filter = PropertyFilter('decimalfield').is_equal_to(random_float)

    response = AppacitiveObject.find('object', query)
    assert response.paging_info.total_records == 1
    assert len(response.objects) == 1


def search_with_bool_property_filter_test():
    obj = AppacitiveObject('object')
    obj.set_property('boolfield', False)
    obj.create()

    query = AppacitiveQuery()
    query.filter = PropertyFilter('boolfield').is_equal_to(False)

    response = AppacitiveObject.find('object', query)
    assert response.paging_info.total_records >= 1
    assert len(response.objects) >= 1


def search_with_like_filter_test():
    obj = AppacitiveObject('object')
    obj.set_property('stringfield', 'mississippi')
    obj.create()

    query = AppacitiveQuery()
    query.filter = PropertyFilter('stringfield').like('*ssissi*')

    response = AppacitiveObject.find('object', query)
    assert len(response.objects) >= 1


#def search_attribute_filter_test():
#    obj = AppacitiveObject('object')
#    obj.set_attribute('Gangnam', 'Style')
#    obj.create()
#
#    query = AppacitiveQuery()
#    query.filter = AttributeFilter('Gangnam').starts_with('St')
#
#    response = AppacitiveObject.find('object', query)
#    assert hasattr(response, 'paging_info')
#    assert response.paging_info.total_records > 0


def search_on_tags_test():
    obj = AppacitiveObject('object')
    obj.add_tags(['sun', 'moon', 'stars'])
    obj.create()

    query = AppacitiveQuery()
    query.filter = TagFilter().match_all(['moon', 'stars'])

    response = AppacitiveObject.find('object', query)
    assert hasattr(response, 'paging_info')
    assert response.paging_info.total_records > 0

    query.filter = TagFilter().match_one_or_more(['stars', 'sky', 'moonlight', 'cloudy'])
    response = AppacitiveObject.find('object', query)
    assert hasattr(response, 'paging_info')
    assert response.paging_info.total_records > 0


def search_with_fields_test():
    random_num1 = get_random_number(5)
    random_num2 = get_random_number(5)
    random_float = float(str(random_num1)+'.'+str(random_num2))
    obj = AppacitiveObject('object')
    obj.set_property('decimalfield', random_float)
    obj.set_property('stringfield', str(random_float))
    obj.create()
    query = AppacitiveQuery()
    query.page_number = 1
    query.page_size = 3
    query.filter = PropertyFilter('decimalfield').is_equal_to(random_float)
    response = AppacitiveObject.find('object', query, ['__createdby', '__revision', 'stringfield'])
    assert hasattr(response, 'objects')
    for obj in response.objects:
        assert obj.get_property('stringfield') is not None
        assert obj.created_by is not None
        assert obj.revision > 0
        assert obj.last_modified_by is None
        assert obj.get_property('intfield') is None


def search_geo_within_circle_test():
    obj = AppacitiveObject('object')
    obj.set_property('geofield', '10.10,20.20')
    obj.create()

    query = AppacitiveQuery()
    query.page_size = 5
    query.filter = GeoFilter('geofield').within_circle('10.10,20.21', '10 mi')

    response = AppacitiveObject.find('object', query)
    assert response.paging_info.total_records > 0


def search_geo_within_polygon_test():
    obj = AppacitiveObject('object')
    obj.set_property('geofield', '10.10,20.20')
    obj.create()

    query = AppacitiveQuery()
    query.page_size = 5
    query.filter = GeoFilter('geofield').within_polygon(['0.0,0.0', '0.0,50.0', '50.0,0.0'])

    response = AppacitiveObject.find('object', query)
    assert response.paging_info.total_records > 0


def search_aggregated_queries_test():
    obj = AppacitiveObject('object')
    obj.set_attribute('Gangnam', 'Style')

    obj.set_property('textfield', '''Karan Arjun is a 1995 Bollywood action thriller film starring
     Raakhee, Shahrukh Khan, Salman Khan, Amrish Puri, Kajol, Mamta Kulkarni and Ranjeet. The film was
      directed by Rakesh Roshan and written by Ravi Kapoor and Sachin Bhowmick.''')

    obj.set_property('stringfield', 'gangnam')
    obj.set_property('intfield', 5)
    obj.create()
    query = AppacitiveQuery()
    filter1 = PropertyFilter('stringfield').is_equal_to('gangnam')
    filter2 = PropertyFilter('intfield').is_greater_than(0)

    filter3 = AttributeFilter('Gangnam').is_equal_to('Style')
    query.free_text_tokens = ['Shahrukh', 'Khan', 'Salman']
    query.filter = BooleanOperator.or_query([filter3, BooleanOperator.and_query([filter1, filter2])])

    response = AppacitiveObject.find('object', query)
    assert response.paging_info.total_records > 0


def search_connected_objects_test():
    obj1 = AppacitiveObject('object')
    obj1.create()
    obj2 = AppacitiveObject('object')

    conn = AppacitiveConnection('sibling').from_existing_object_id('object', obj1.id).to_new_object('object', obj2)
    conn.create()
    conn2 = AppacitiveConnection('sibling').from_existing_object_id('object', obj1.id).to_new_object('object', AppacitiveObject('object'))
    conn2.create()
    response = AppacitiveConnection.find_connected_objects('sibling', 'object', obj1.id)
    assert hasattr(response, 'objects')
    assert len(response.objects) == 2


def search_connections_for_objects_test():
    conn = AppacitiveConnection('sibling').from_new_object('object', AppacitiveObject('object')).to_new_object('object', AppacitiveObject('object'))
    conn.create()

    response = AppacitiveConnection.find_by_objects(conn.endpoint_a.objectid, conn.endpoint_b.objectid)
    assert hasattr(response, 'connections')
    assert len(response.connections) == 1

    response = AppacitiveConnection.find_by_objects_and_relation(conn.endpoint_a.objectid, conn.endpoint_b.objectid, 'sibling')
    assert hasattr(response, 'connection')
    assert response.connection.id == conn.id


def search_objects_between_two_objects_test():
    pass


def query_dsl_test():
    assert str(PropertyFilter('p').is_not_equal_to('v')) == "*p != 'v'"
    assert str(PropertyFilter('p').is_greater_than('v')) == "*p > 'v'"
    assert str(PropertyFilter('p').is_less_than('v')) == "*p < 'v'"
    assert str(PropertyFilter('p').is_greater_than_equal_to('v')) == "*p >= 'v'"
    assert str(PropertyFilter('p').is_less_than_equal_to('v')) == "*p <= 'v'"

    assert str(AttributeFilter('a').ends_with('v')) == "@a like '*v'"
    assert str(AttributeFilter('a').starts_with('v')) == "@a like 'v*'"