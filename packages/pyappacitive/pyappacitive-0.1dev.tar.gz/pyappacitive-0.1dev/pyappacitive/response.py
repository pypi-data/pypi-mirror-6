__author__ = 'sathley'


#class Status(object):
#    def __init__(self, status=None):
#        self.code = None
#        self.message = None
#        self.additional_messages = None
#        self.reference_id = None
#        self.version = None
#
#        if status is not None:
#            self.code = status.get('code', 0)
#            self.message = status.get('message', None)
#            self.additional_messages = status.get('additionalmessages', [])
#            self.reference_id = status['referenceid']
#            self.version = status['version']


class PagingInfo(object):
    def __init__(self, paging_info=None):
        self.page_number = 0
        self.page_size = 0
        self.total_records = 0

        if paging_info is not None:
            self.page_number = paging_info['pagenumber']
            self.page_size = paging_info['pagesize']
            self.total_records = paging_info['totalrecords']


class AppacitiveResponse(object):
    def __init__(self, paging_info=None):
        if paging_info is not None:
            self.paging_info = PagingInfo(paging_info)



