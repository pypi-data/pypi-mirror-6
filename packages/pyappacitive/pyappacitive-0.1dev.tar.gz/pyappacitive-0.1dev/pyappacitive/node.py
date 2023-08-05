__author__ = 'sathley'


class GraphNode(object):
    def __init__(self, node=None):
        self.object = None
        self.connection = None
        self.children = {}
        self.parent = None

    def add_child_node(self, name, node):
        val = self.children.get(name, None)

        if val is None:
            self.children[name] = []

        self.children[name].append(node)

    def get_children(self, name):
        return self.children.get(name, [])









