__author__ = 'sathley'

from pyappacitive import AppacitiveGraphSearch, AppacitiveObject, AppacitiveConnection
import nose, random


def get_random_string(number_of_characters=10):
    arr = [str(i) for i in range(number_of_characters)]
    random.shuffle(arr)
    return ''.join(arr)


def projection_test():
    val1 = get_random_string()
    val2 = get_random_string()
    root = AppacitiveObject('object')
    root.create()

    level1child = AppacitiveObject('object')
    level1child.set_property('stringfield', val1)
    level1child.create()

    level1edge = AppacitiveConnection('link')
    level1edge.endpoint_a.label = 'parent'
    level1edge.endpoint_a.objectid = root.id
    level1edge.endpoint_b.label = 'child'
    level1edge.endpoint_b.objectid = level1child.id
    level1edge.create()

    level2child = AppacitiveObject('object')
    level2child.set_property('stringfield', val2)
    level2child.create()

    level2edge = AppacitiveConnection('link')
    level2edge.endpoint_a.label = 'parent'
    level2edge.endpoint_a.objectid = level1child.id
    level2edge.endpoint_b.label = 'child'
    level2edge.endpoint_b.objectid = level2child.id
    level2edge.create()

    response = AppacitiveGraphSearch.project('sample_project', [root.id], {'level1_filter': val1, 'level2_filter': val2})
    assert len(response.nodes) == 1
    assert response.nodes[0].object is not None
    assert response.nodes[0].object.id == root.id
    level1children = response.nodes[0].get_children('level1_children')
    assert len(level1children) == 1
    assert level1children[0].object is not None
    assert level1children[0].object.id == level1child.id
    assert level1children[0].connection is not None
    assert level1children[0].connection.id == level1edge.id
    assert level1children[0].connection.endpoint_a.objectid == root.id
    assert level1children[0].connection.endpoint_b.objectid == level1child.id

    level2children = level1children[0].get_children('level2_children')
    assert len(level2children) == 1
    assert level2children[0].object is not None
    assert level2children[0].object.id == level2child.id
    assert level2children[0].connection is not None
    assert level2children[0].connection.id == level2edge.id
    assert level2children[0].connection.endpoint_a.objectid == level1child.id
    assert level2children[0].connection.endpoint_b.objectid == level2child.id


def filter_test():

    parent = AppacitiveObject('object')
    parent.create()
    unique = get_random_string()
    child = AppacitiveObject('object')
    child.set_property('stringfield', unique)
    conn = AppacitiveConnection('link')
    conn.endpoint_a.label = 'parent'
    conn.endpoint_a.objectid = parent.id

    conn.endpoint_b.label = 'child'
    conn.endpoint_b.object = child
    conn.create()

    response = AppacitiveGraphSearch.filter('sample_filter', {'search_value': unique})
    assert len(response.ids) == 1
    assert response.ids[0] == parent.id
