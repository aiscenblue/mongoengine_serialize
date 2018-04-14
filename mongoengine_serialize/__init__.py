from mongoengine.base import BaseDocument
from bson.objectid import ObjectId
from datetime import datetime
from mongoengine.queryset.queryset import QuerySet


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

    def __init__(self, collections):
        self.__raw_collections = collections
        self.__collections = self.__serialize_collection(collections)


    def __call__(self, collections):
        self.__raw_collections = collections
        serialized_collection = self.__serialize_collection(collections)
        return self

    def __serialize_type_of(self, collection):
        if isinstance(collection, BaseDocument):
            return self.__filter_serialize(collection.to_mongo())
        elif isinstance(collection, JsonSerialized):
            return collection
        else:
            return collection

    def __serialize_collection(self, collections):
        if isinstance(collections, QuerySet) or isinstance(collections, list):
            return [self.__serialize_collection(_) for _ in collections]
        else:
            return self.__serialize_type_of(collections)

    def __get_raw_name(self, name):
        if name == "id":
            return "_id"
        else:
            return name

    def __filter_serialize(self, collections):
        if isinstance(collections, dict):
            new_collection = dict()
            for index, collection in enumerate(collections.items()):
                key, value = collection
                raw_collection = getattr(self.__raw_collections, self.__get_raw_name(key), collection)
                if isinstance(value, list) or isinstance(value, dict):
                    re_serialize = Serialize(raw_collection).jsonify()
                    if isinstance(re_serialize, tuple):
                        new_key, new_value = Serialize(raw_collection).jsonify()
                        new_collection.update(dict.fromkeys((new_key,), new_value))
                    else:
                        new_collection.update(dict.fromkeys((key, ), re_serialize))
                else:
                    new_collection.update(self.__serialize(key, value))
            return new_collection
        else:
            return collections

    def __serialize(self, key, value):
        serialized_attribute = self.__attribute_serialize(key, value)
        altered_serialized = self.alter_after_serialize_attributes(serialized_attribute)
        new_key, new_value = altered_serialized if altered_serialized else serialized_attribute
        return JsonSerialized(**dict.fromkeys((new_key,), new_value)).to_json()

    """ 
        alter each collection before returning
    """
    def alter_after_serialize_attributes(self, collection):
        return collection

    def exclude(self, *attributes):
        for attribute in attributes:
            if hasattr(self.__collections, attribute):
                delattr(self.__collections, attribute)
        return self

    @staticmethod
    def __to_string_attribute(attr):
        return str(attr)

    def __attribute_serialize(self, key, val):
        if isinstance(val, ObjectId):
            if key == "_id":
                return "id", self.__to_string_attribute(val)
            else:
                return key, self.__to_string_attribute(val)
        elif isinstance(val, datetime):
            return key, self.__to_string_attribute(val)
        else:
            return key, val

    def raw(self):
        return self.__raw_collections

    @staticmethod
    def __dict_jsonify(collection):
        if isinstance(collection, JsonSerialized):
            return collection.to_json()
        else:
            return collection

    def jsonify(self):
        collections = self.__collections
        if isinstance(collections, list):
            return [self.__dict_jsonify(_) for _ in collections]
        elif isinstance(collections, dict):
            return self.__dict_jsonify(collections)
        else:
            return self.__dict_jsonify(collections)