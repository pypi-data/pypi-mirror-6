from .utilities import http, urlfactory
__author__ = 'sathley'

from .entity import AppacitiveEntity
from .error import *
from .utilities import customjson
from .response import AppacitiveResponse
import logging

# conn create from object /to object should initialize sent object
# add file upload support using urllib2
# complete object base
# run pylint, pyflakes, sphynx


object_logger = logging.getLogger(__name__)
object_logger.addHandler(logging.NullHandler())


class AppacitiveObject(AppacitiveEntity):

    def __init__(self, obj):

        self.type = None
        self.type_id = 0

        if isinstance(obj, str):
            super(AppacitiveObject, self).__init__()
            self.type = obj
            return
        if isinstance(obj, int):
            super(AppacitiveObject, self).__init__()
            self.type_id = obj
            return

        super(AppacitiveObject, self).__init__(obj)
        if obj is not None:
            self.type = obj.get('__type', None)
            self.type_id = int(obj.get('__typeid', 0))

    def _set_self(self, obj):

        super(AppacitiveObject, self)._set_self(obj)

        self.type = obj.get('__type', None)
        self.type_id = int(obj.get('__typeid', 0))

    def get_dict(self):

        native = super(AppacitiveObject, self).get_dict()

        if self.type is not None:
            native['__type'] = self.type

        if self.type_id is not None:
            native['__typeid'] = str(self.type_id)

        return native

    def create(self):

        if self.type is None and self.type_id <= 0:
            raise ValidationError('Provide at least one among type name or type id.')

        url = urlfactory.object_urls["create"](self.type if self.type is not None else self.type_id)
        headers = urlfactory.get_headers()
        object_logger.info('Creating object')
        api_resp = http.put(url, headers, customjson.serialize(self.get_dict()))
        self._set_self(api_resp['object'])
        self._reset_update_commands()

    def delete(self):

        if self.type is None and self.type_id <= 0:
            raise ValidationError('Provide at least one among type name or type id.')

        if self.id <= 0:
            raise ValidationError('Object id is missing.')

        url = urlfactory.object_urls["delete"](self.type if self.type is not None else self.type_id, self.id)
        headers = urlfactory.get_headers()
        object_logger.info('Deleting object')
        http.delete(url, headers)

    def delete_with_connections(self):

        if self.type is None and self.type_id <= 0:
            raise ValidationError('Provide at least one among type name or type id.')

        if self.id <= 0:
            raise ValidationError('Object id is missing.')

        url = urlfactory.object_urls["delete_with_connections"](self.type if self.type is not None else self.type_id,
                                                               self.id)
        headers = urlfactory.get_headers()
        object_logger.info('Deleting object with connections')
        http.delete(url, headers)

    @classmethod
    def multi_delete(cls, object_type, object_ids):

        if object_type is None:
            raise ValidationError('Type is missing.')

        if object_ids is None:
            raise ValidationError('Object ids are missing.')

        url = urlfactory.object_urls["multidelete"](object_type)
        headers = urlfactory.get_headers()

        payload = {"idlist": []}
        for object_id in object_ids:
            payload["idlist"].append(str(object_id))
        object_logger.info('Deleting multiple objects')
        http.post(url, headers, customjson.serialize(payload))

    def update(self, with_revision=False):

        if self.type is None and self.type_id <= 0:
            raise ValidationError('Provide at least one among type name or type id.')

        if self.id <= 0:
            raise ValidationError('Object id is missing.')
        url = urlfactory.object_urls["update"](self.type if self.type is not None else self.type_id, self.id)

        if with_revision:
            url += '?revision=' + self.revision

        headers = urlfactory.get_headers()
        payload = self.get_update_command()
        object_logger.info('Updating object')
        api_resp = http.post(url, headers, customjson.serialize(payload))
        self._set_self(api_resp['object'])

    @classmethod
    def get(cls, object_type, object_id, fields=None):

        if object_type is None:
            raise ValidationError('Type is missing.')

        if object_id is None:
            raise ValidationError('Object id is missing.')

        url = urlfactory.object_urls["get"](object_type, object_id, fields)
        if fields is not None:
            url += '?fields=' + ','.join(fields)
        headers = urlfactory.get_headers()
        api_response = http.get(url, headers)
        object_logger.info('Fetching object')
        response = AppacitiveResponse()
        response.object = cls(api_response['object'])
        return response

    def fetch_latest(self):
        url = urlfactory.object_urls["get"](self.type, self.id)
        headers = urlfactory.get_headers()
        object_logger.info('Fetching latest object')
        api_response = http.get(url, headers)
        self._set_self(api_response['object'])
        self._reset_update_commands()

    @classmethod
    def multi_get(cls, object_type, object_ids, fields=None):

        if object_type is None:
            raise ValidationError('Type is missing.')

        if object_ids is None:
            raise ValidationError('Object ids are missing.')

        url = urlfactory.object_urls["multiget"](object_type, object_ids, fields)

        headers = urlfactory.get_headers()
        object_logger.info('Fetching multiple objects')
        api_response = http.get(url, headers)

        response = AppacitiveResponse()

        api_objects = api_response.get('objects', [])

        return_objects = []
        for obj in api_objects:
            appacitive_object = cls(obj)
            return_objects.append(appacitive_object)
        response.objects = return_objects
        return response

    @classmethod
    def find(cls, object_type, query, fields=None):

        if object_type is None:
            raise ValidationError('Type is missing.')

        url = urlfactory.object_urls["find_all"](object_type, query, fields)
        headers = urlfactory.get_headers()
        object_logger.info('Searching objects')
        api_response = http.get(url, headers)

        response = AppacitiveResponse(api_response['paginginfo'])
        api_objects = api_response.get('objects', [])

        return_objects = []
        for obj in api_objects:
            appacitive_object = cls(obj)
            return_objects.append(appacitive_object)
        response.objects = return_objects
        return response

    @classmethod
    def find_in_between_two_objects(cls, object_type, object_a_id, relation_a, label_a, object_b_id, relation_b, label_b, fields=None):

        if object_type is None:
            raise ValidationError('Type is missing.')

        url = urlfactory.object_urls["find_between_two_objects"](object_type, object_a_id, relation_a, label_a, object_b_id, relation_b, label_b, fields)

        headers = urlfactory.get_headers()
        api_response = http.get(url, headers)
        object_logger.info('Searching objects between two objects')
        response = AppacitiveResponse(api_response['paginginfo'])

        api_objects = api_response.get('objects', [])

        return_objects = []
        for obj in api_objects:
            appacitive_object = cls(obj)
            return_objects.append(appacitive_object)
        response.objects = return_objects
        return response


