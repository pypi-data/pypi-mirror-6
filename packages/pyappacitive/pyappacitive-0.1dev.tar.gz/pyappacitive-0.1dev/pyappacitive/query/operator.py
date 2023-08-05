__author__ = 'sathley'


class BooleanOperator(object):
    def __init__(self, inner_queries, operator=None):
        self.operator = operator
        self.inner_queries = inner_queries

    @classmethod
    def and_query(cls, inner_queries):
        return cls(inner_queries, 'and')

    @classmethod
    def or_query(cls, inner_queries):
        return cls(inner_queries, 'or')

    def __repr__(self):
        opening_bracket = '( '
        closing_bracket = ' )'
        joining_string = ' {0} '.format(self.operator)
        result = opening_bracket + joining_string.join(self.__get_string_representation(self.inner_queries)) + closing_bracket
        return result

    @staticmethod
    def __get_string_representation(queries):
        return (str(query) for query in queries if query is not None)
