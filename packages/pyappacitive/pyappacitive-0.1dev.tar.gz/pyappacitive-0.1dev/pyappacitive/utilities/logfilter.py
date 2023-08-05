__author__ = 'sathley'
import logging


class SlowCallLogFilter(logging.Filter):
    def __init__(self, duration):
        super(SlowCallLogFilter, self).__init__()
        self.duration = duration

    def filter(self, rec):
        if hasattr(rec, 'TIME_TAKEN') is False:
            return True
        if rec.TIME_TAKEN >= self.duration:
            return True
        else:
            return False


class FailedRequestsLogFilter(logging.Filter):

    def filter(self, rec):
        if hasattr(rec, 'RESPONSE') is False:
            return True
        status = rec.RESPONSE.get('status', None)
        if status is not None and status["code"] == '200':
            return False
        else:
            return True