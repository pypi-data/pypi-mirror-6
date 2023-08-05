__author__ = 'sathley'

from .utilities import http, urlfactory
from .utilities import customjson
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class AppacitiveEmail(object):
    def __init__(self):
        pass

    @staticmethod
    def send_raw_email(to, subject, body, cc=[], bcc=[], is_body_html=False, smtp=None, from_email=None, reply_to_email=None):
        payload = {}
        payload['to'] = to
        payload['cc'] = cc
        payload['bcc'] = bcc
        payload['subject'] = subject
        payload['body'] = {
            'content': body,
            'ishtml': is_body_html
        }

        if smtp is not None:
            payload['smtp'] = smtp
        if from_email is not None:
            payload['from'] = from_email
        if reply_to_email is not None:
            payload['replyto'] = reply_to_email

        url = urlfactory.email_urls["send"]()
        headers = urlfactory.get_headers()

        http.post(url, headers, customjson.serialize(payload))

    @staticmethod
    def send_templated_email(to, subject, template_name, template_fillers, cc=[], bcc=[], is_body_html=False, smtp=None, from_email=None, reply_to_email=None):
        payload = {}
        payload['to'] = to
        payload['cc'] = cc
        payload['bcc'] = bcc
        payload['subject'] = subject
        payload['body'] = {
            'templatename': template_name,
            'data': template_fillers,
            'ishtml': is_body_html
        }

        if smtp is not None:
            payload['smtp'] = smtp
        if from_email is not None:
            payload['from'] = from_email
        if reply_to_email is not None:
            payload['replyto'] = reply_to_email

        url = urlfactory.email_urls["send"]()
        headers = urlfactory.get_headers()

        http.post(url, headers, customjson.serialize(payload))


