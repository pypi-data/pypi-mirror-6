__author__ = 'sathley'

from . import AppacitiveObject, AppacitiveConnection, GraphNode
import types


def convert_node(node):
    return parse_graph_node(None, None, None, node)


def parse_graph_node(parent, name, parent_label, node):

        # parse article
        current = GraphNode()
        node_clone = node.copy()
        for k, __ in node.iteritems():
            if k == '__edge' or k == '__children':
                node_clone.pop(k)
        current.object = AppacitiveObject(node_clone)

        if parent is not None:
            edge = node.get('__edge', None)
            if edge is not None:
                edge_clone = edge.copy()
                current.connection = parse_connection(parent_label, parent.object, current.object, edge_clone)

        children = node.get('__children', None)
        if children is not None:
            for k, v in children.iteritems():
                if isinstance(v, types.DictionaryType):
                    parse_child_nodes(k, v, current)

        if parent is not None:
            parent.add_child_node(name, current)

        return current


def parse_child_nodes(name, d, current):
        parent_label = d.get('parent', None)
        values = d['values']
        if isinstance(values, types.ListType):
            for value in values:
                parse_graph_node(current, name, parent_label, value)


def parse_connection(parent_label, parent_object, current_object, d):

    label = d.get('__label', None)
    relation_type = d.get('__relationtype', None)
    conn_id = int(d.get('__id', 0))

    connection = AppacitiveConnection(d)
    connection.relation_type = relation_type
    connection.id = conn_id
    connection.endpoint_a.label = parent_label
    connection.endpoint_a.object = parent_object
    connection.endpoint_a.objectid = parent_object.id

    connection.endpoint_b.label = label
    connection.endpoint_b.object = current_object
    connection.endpoint_b.objectid = current_object.id

    return connection