__author__ = 'sathley'

import types


class AppacitiveQuery(object):

    def __init__(self):

        self.page_number = None
        self.page_size = None

        self.order_by = None
        self.is_ascending = None

        self.free_text_tokens = []
        self.free_text_language = None
        self.language = None

        self.filter = None

    def __repr__(self):
        items = []
        if self.page_number is not None:
            if isinstance(self.page_number, int) is False:
                raise TypeError('Invalid value for page_number. It should be a integer.')
            items.append('pNum='+str(self.page_number))

        if self.page_size is not None:
            if isinstance(self.page_size, int) is False:
                raise TypeError('Invalid value for page_size. It should be a integer.')
            items.append('pSize='+str(self.page_size))

        if self.order_by is not None:
            items.append('orderBy='+self.order_by)

        if self.is_ascending is not None:
            if isinstance(self.is_ascending, bool) is False:
                raise TypeError('Invalid value for isAscending. It should be a bool.')
            items.append('isAsc='+str(self.is_ascending))

        if len(self.free_text_tokens) > 0:
            if self.free_text_language is not None:
                items.append(('language={0}&freetext={1}'.format(self.language, ','.join(self.free_text_tokens))))
            else:
                items.append('freetext='+','.join(self.free_text_tokens))

        if self.filter is not None:
            items.append('query='+str(self.filter))

        return '&'.join(items)


