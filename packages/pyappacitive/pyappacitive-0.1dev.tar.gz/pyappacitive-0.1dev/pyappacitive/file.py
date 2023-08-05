__author__ = 'sathley'

from .utilities import urlfactory, http
from .error import ValidationError
from .response import AppacitiveResponse
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class AppacitiveFile(object):
    def __init__(self):
        pass

    @staticmethod
    def get_upload_url(content_type, filename=None, expires=None):

        if content_type is None:
            raise ValidationError('content-type is mandatory for file upload.')

        url = urlfactory.file_urls['get_upload_url'](content_type)

        if filename is not None:
            url += '&filename='+filename
        if expires is not None:
            url += '&expires='+expires

        headers = urlfactory.get_headers()
        logging.info('Getting upload URL')
        api_response = http.get(url, headers)
        response = AppacitiveResponse()
        response.id = api_response['id']
        response.url = api_response['url']
        return response

    @staticmethod
    def get_download_url(file_id, expires=None):

        if file_id is None:
            raise ValidationError('file id is mandatory for file download.')

        url = urlfactory.file_urls['get_download_url'](file_id)

        if expires is not None:
            url += '?expires='+expires

        headers = urlfactory.get_headers()
        logging.info('Getting download URL')
        api_response = http.get(url, headers)
        response = AppacitiveResponse()
        response.url = api_response['uri']
        return response

    @staticmethod
    def delete_file(file_id):

        if file_id is None:
            raise ValidationError('file id is mandatory for file delete.')

        url = urlfactory.file_urls['file_delete'](file_id)

        headers = urlfactory.get_headers()
        logging.info('Deleting file')
        http.delete(url, headers)


