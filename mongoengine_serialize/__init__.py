from mongoengine.base import BaseDocument
from bson.objectid import ObjectId
from datetime import datetime

# TODO :: serialize lists type, nested serialization


class JsonSerialized:

    def __init__(self, **entities):
        for key, value in entities.items():
            setattr(self, key, value)

    def exclude_attributes(self, *attributes):
        for attribute in attributes:
            if hasattr(self, attribute):
                delattr(self, attribute)
        return self

    def to_json(self):
        return self.__dict__


class Serialize:
    __collections = dict()

    def __init__(self, data):
        self.collections = data
        self.__filter_set_attribute()

    def __call__(self, data):
        self.collections = data
        self.__filter_set_attribute()
        return self

    @property
    def collections(self):
        return self.__collections

    # filter collection as a valid mongodb document
    @collections.setter
    def collections(self, collections):
        self.__collections = self.__resurse_collections(collections)

    def __resurse_collections(self, collections):
        if isinstance(collections, list):
            col_list = list()
            for collection in collections:
                if isinstance(collection, list):
                    col_list.append(self.__validate_collection(collection))
                else:
                    col_list.append(self.__validate_collection(collection))
            return col_list
        else:
            return self.__validate_collection(collections)

    # TODO :: loop all attributes and check if there are other baseDocuments
    @staticmethod
    def __validate_collection(collection):
        if isinstance(collection, BaseDocument):
            return collection.to_mongo()
        elif isinstance(collection, JsonSerialized):
            return collection
        else:
            return collection

    def __filter_set_attribute(self):
        if isinstance(self.collections, list):
            col = list()
            for collection in self.collections:
                col.append(self.__serialize(collection))
                self.collections = col
        else:
            self.collections = self.__serialize(self.collections)

    def __serialize(self, collection):
        if isinstance(collection, dict):
            json_serialized = JsonSerialized()
            for key, value in collection.items():
                if isinstance(value, list):
                    for col in value:
                        val_list = list()
                        value_dict = dict.fromkeys((key,), col)
                        val_list.append(self.__serialize(value_dict).to_json())
                        setattr(json_serialized, key, val_list)
                else:
                    serialized_attribute = self.__attribute_serialize(key, value)
                    altered_serialized = self.alter_after_serialize_attributes(serialized_attribute)
                    if not altered_serialized:
                        raise ValueError(
                            self.alter_after_serialize_attributes.__name__ + "should return a non null value")
                    new_key, new_value = altered_serialized
                    setattr(json_serialized, new_key, new_value)
            return json_serialized
        else:
            raise ValueError('Cannot serialize object.')

    """ 
        alter each collection before returning
    """
    def alter_after_serialize_attributes(self, collection):
        return collection

    def exclude(self, *attributes):
        for attribute in attributes:
            if hasattr(self.collections, attribute):
                delattr(self.collections, attribute)
        return self

    @staticmethod
    def __attribute_serialize(key, val):
        if isinstance(val, ObjectId):
            return "id", str(val)
        elif isinstance(val, datetime):
            return key, str(val)
        else:
            return key, val

    def raw(self):
        return self.collections

    def jsonify(self):
        if isinstance(self.collections, list):
            for collection in self.collections:
                collection.to_json()
            return self.collections
        else:
            return self.collections.to_json()
