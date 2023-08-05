__author__ = 'sathley'

from .utilities import urlfactory, http, customjson
from .error import ValidationError
from .response import AppacitiveResponse
import json, logging

push_logger = logging.getLogger(__name__)
push_logger.addHandler(logging.NullHandler())


class AppacitivePushNotification(object):
    def __init__(self, push=None):

        if push is not None:
            self.id = int(push.get('id', 0))
            self.isbroadcast = push.get('isbroadcast', None)
            self.alert = push.get('alert', None)
            self.badge = push.get('badge', None)
            self.expireafter = int(push.get('expireafter', 0))
            self.devicecount = int(push.get('devicecount', 0))
            self.successfulcount = int(push.get('successfulcount', 0))
            self.failurecount = int(push.get('failurecount', 0))
            self.status = push.get('status', None)
            self.timestamp = push.get('timestamp', None)
            self.lastmodifieddate = push.get('lastmodifieddate', None)
            self.customdata = push.get('customdata', {})
            self.devicedata = push.get('devicedata', {})
        else:
            self.id = 0
            self.isbroadcast = None
            self.alert = None
            self.badge = None
            self.expireafter = None
            self.customdata = {}
            self.devicedata = {}
            self.devicecount = 0
            self.successfulcount = 0
            self.failurecount = 0
            self.status = None
            self.timestamp = None
            self.lastmodifieddate = None

    @staticmethod
    def broadcast(data, platform_options=None, expire_after=None):
        push_request = {
            'broadcast': True
        }

        if platform_options is not None:
            push_request['platformoptions'] = platform_options

        if data is not None:
            push_request['data'] = data

        if expire_after is not None:
            push_request['expire_after'] = expire_after

        url = urlfactory.push_urls['send']()
        headers = urlfactory.get_headers()

        payload = json.dumps(push_request)
        push_logger.info('Send Push notification')
        api_response = http.post(url, headers, payload)
        response = AppacitiveResponse()
        response.id = int(api_response['id'])
        return response

    @staticmethod
    def send_to_channels(channels, data, platform_options=None, expire_after=None):
        push_request = {
            'channels': channels
        }

        if platform_options is not None:
            push_request['platformoptions'] = platform_options

        if data is not None:
            push_request['data'] = data

        if expire_after is not None:
            push_request['expire_after'] = expire_after

        url = urlfactory.push_urls['send']()
        headers = urlfactory.get_headers()

        payload = json.dumps(push_request)
        push_logger.info('Send Push notification')
        api_response = http.post(url, headers, payload)
        response = AppacitiveResponse()
        response.id = int(api_response['id'])
        return response

    @staticmethod
    def send_to_specific_devices(device_ids, data, platform_options=None, expire_after=None):
        push_request = {
            'deviceids': device_ids
        }

        if platform_options is not None:
            push_request['platformoptions'] = platform_options

        if data is not None:
            push_request['data'] = data

        if expire_after is not None:
            push_request['expire_after'] = expire_after

        url = urlfactory.push_urls['send']()
        headers = urlfactory.get_headers()

        payload = json.dumps(push_request)
        push_logger.info('Send Push notification')
        api_response = http.post(url, headers, payload)
        response = AppacitiveResponse()
        response.id = int(api_response['id'])
        return response

    @staticmethod
    def send_using_query(query, data, platform_options=None, expire_after=None):
        push_request = {
            'query': str(query)
        }

        if platform_options is not None:
            push_request['platformoptions'] = platform_options

        if data is not None:
            push_request['data'] = data

        if expire_after is not None:
            push_request['expire_after'] = expire_after

        url = urlfactory.push_urls['send']()
        headers = urlfactory.get_headers()

        payload = json.dumps(push_request)
        push_logger.info('Send Push notification')
        api_response = http.post(url, headers, payload)
        response = AppacitiveResponse()
        response.id = int(api_response['id'])
        return response

    @staticmethod
    def get_notification_by_id(notification_id):

        if notification_id is None:
            raise ValidationError('Notification id is required to fetch push notification.')

        url = urlfactory.push_urls['get'](notification_id)
        headers = urlfactory.get_headers()
        push_logger.info('Fetch Push notification')
        api_response = http.get(url, headers)
        response = AppacitiveResponse()
        response.notification = AppacitivePushNotification(api_response['pushnotification'])
        return response

    @staticmethod
    def get_all_notification():

        url = urlfactory.push_urls['get_all']()
        headers = urlfactory.get_headers()
        push_logger.info('Fetch all notifications')
        api_response = http.get(url, headers)
        response = AppacitiveResponse()

        return_notifications = []
        for notification in api_response['pushnotifications']:
            if notification:
                return_notifications.append(AppacitivePushNotification(notification))
        response.notifications = return_notifications
        return response


