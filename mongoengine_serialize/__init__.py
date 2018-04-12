from mongoengine.base import BaseDocument
from bson.objectid import ObjectId
from datetime import datetime


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
        serialized_collection = self.__serialize_collection(collections)
        self.__collections = self.__resurse_collections(serialized_collection)

    def __call__(self, collections):
        self.__raw_collections = collections
        serialized_collection = self.__serialize_collection(collections)
        self.__collections = self.__resurse_collections(serialized_collection)
        return self

    def __resurse_collections(self, collections):
        if isinstance(collections, list):
            col_list = list()
            for collection in collections:
                if isinstance(collection, list):
                    col_list.append(self.__serialize(collection))
                else:
                    col_list.append(self.__serialize(collection))
            return col_list
        else:
            return self.__serialize(collections)

    @staticmethod
    def __serialize_collection(collection):
        if isinstance(collection, BaseDocument):
            return collection.to_mongo()
        elif isinstance(collection, JsonSerialized):
            return collection
        else:
            return collection

    def __filter_set_attribute(self, collection):
        collections = self.__resurse_collections(collection)
        if isinstance(collections, list):
            col = list()
            for collection in collections:
                col.append(self.__serialize(collection))
                collections = col
        else:
            collections = self.__serialize(collections)
        return collections

    def __serialize(self, collection):
        if isinstance(collection, dict):
            json_serialized = JsonSerialized()
            for key, value in collection.items():
                if isinstance(value, list):
                    val_list = list()
                    for index, _ in enumerate(value):
                        raw_collection = getattr(self.__raw_collections, key)
                        val_list.append(Serialize(raw_collection[index]).jsonify())
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
            if hasattr(self.__collections, attribute):
                delattr(self.__collections, attribute)
        return self

    @staticmethod
    def __attribute_serialize(key, val):
        if isinstance(val, ObjectId):
            if key == "_id":
                return "id", str(val)
            else:
                return key, str(val)
        elif isinstance(val, datetime):
            return key, str(val)
        else:
            return key, val

    def raw(self):
        return self.__raw_collections

    def jsonify(self):
        collections = self.__collections
        if isinstance(collections, list):
            for collection in collections:
                collection.to_json()
            return collections
        else:
            return collections.to_json()
