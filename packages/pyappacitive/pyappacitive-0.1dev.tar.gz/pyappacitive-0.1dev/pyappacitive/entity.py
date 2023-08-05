__author__ = 'sathley'
from abc import ABCMeta

connection_system_properties = ['__relationtype', '__relationid', '__id', '__createdby', '__lastmodifiedby',
                                '__utcdatecreated', '__utclastupdateddate', '__tags', '__attributes', '__properties',
                                '__revision', '__endpointa', '__endpointb']

object_system_properties = ['__type', '__typeid', '__id', '__createdby', '__lastmodifiedby', '__utcdatecreated',
                            '__utclastupdateddate', '__tags', '__attributes', '__properties', '__revision']


class AppacitiveEntity(object):

    __metaclass__ = ABCMeta

    def __init__(self, entity=None):
        self.__properties = {}
        self.__attributes = {}
        self.__tags = []
        self.id = 0
        self.revision = 0
        self.created_by = None
        self.utc_date_created = None
        self.utc_last_updated_date = None
        self.last_modified_by = None

        # update observers
        self.__properties_changed = {}
        self.__attributes_changed = {}
        self.__tags_added = []
        self.__tags_removed = []

        if entity is not None:

            self.id = int(entity.get('__id', 0))
            self.created_by = entity.get('__createdby', None)
            self.last_modified_by = entity.get('__lastmodifiedby', None)
            self.utc_date_created = entity.get('__utcdatecreated', None)
            self.utc_last_updated_date = entity.get('__utclastupdateddate', None)
            self.__tags = entity.get('__tags', None)
            self.__attributes = entity.get('__attributes', None)
            self.revision = int(entity.get('__revision', 0))

            for k, v in entity.iteritems():
                if k not in connection_system_properties:
                    self.__properties[k] = v

    def _set_self(self, obj):

        if obj is None:
            return

        self.id = int(obj.get('__id', 0))
        self.created_by = obj.get('__createdby', None)
        self.last_modified_by = obj.get('__lastmodifiedby', None)
        self.utc_date_created = obj.get('__utcdatecreated', None)
        self.utc_last_updated_date = obj.get('__utclastupdateddate', None)
        self.__tags = obj.get('__tags', None)
        self.__attributes = obj.get('__attributes', None)
        self.revision = int(obj.get('__revision', 0))
        for k, v in obj.iteritems():
            if k not in object_system_properties:
                self.__properties[k] = v

    def get_dict(self):
        native = {}

        if self.id is not None:
            native['__id'] = str(self.id)

        if self.revision is not 0:
            native['__revision'] = str(self.revision)

        if self.created_by is not None:
            native['__createdby'] = self.created_by

        if self.last_modified_by is not None:
            native['__lastmodifiedby'] = self.last_modified_by

        if self.utc_date_created is not None:
            native['__utcdatecreated'] = self.utc_date_created

        if self.utc_last_updated_date is not None:
            native['__utclastupdateddate'] = self.utc_last_updated_date

        tags = self.get_all_tags()
        if tags is not None:
            native['__tags'] = tags

        native['__attributes'] = self.__attributes

        native.update(self.__properties)
        return native

    def get_all_properties(self):
        return self.__properties

    def get_all_attributes(self):
        return self.__attributes

    def get_all_tags(self):
        return self.__tags

    def set_property(self, property_name, property_value):
        self.__properties[property_name] = property_value
        self.__properties_changed[property_name] = property_value

    def get_property(self, property_name):
        return self.__properties.get(property_name, None)

    def remove_property(self, property_name):
        self.set_property(property_name, None)

    def set_attribute(self, attribute_key, attribute_value):
        self.__attributes[attribute_key] = attribute_value
        self.__attributes_changed[attribute_key] = attribute_value

    def get_attribute(self, attribute_key):
        return self.__attributes.get(attribute_key, None)

    def remove_attribute(self, attribute_key):
        if attribute_key in self.__attributes:
            self.set_attribute(attribute_key, None)

    def add_tag(self, tag):
        if tag not in self.__tags:
            self.__tags.append(tag)
            self.__tags_added.append(tag)

    def add_tags(self, tags):
        for tag in tags:
            if tag not in self.__tags:
                self.__tags.append(tag)
                self.__tags_added.append(tag)

    def remove_tag(self, tag):
        if tag in self.__tags:
            self.__tags.remove(tag)
            self.__tags_removed.append(tag)

    def remove_tags(self, tags):
        for tag in tags:
            if tag in self.__tags:
                self.__tags.remove(tag)
                self.__tags_removed.append(tag)

    def tag_exists(self, tag):
        return tag in self.__tags

    def get_update_command(self):
        update_command = {}
        update_command['__addtags'] = self.__tags_added
        update_command['__removetags'] = self.__tags_removed
        update_command['__attributes'] = self.__attributes_changed
        for k, v in self.__properties_changed.iteritems():
            update_command[k] = v
        return update_command

    def _reset_update_commands(self):
        # reset observers
        self.__properties_changed = {}
        self.__attributes_changed = {}
        self.__tags_added = []
        self.__tags_removed = []

