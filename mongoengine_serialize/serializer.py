from mongoengine.base import BaseDocument
from mongoengine.base.datastructures import LazyReference
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
        self.__collections = self.__serialize_collection(collections)
        return self

    def __serialize_type_of(self, collection):
        if isinstance(collection, BaseDocument):
            return collection.to_mongo(), collection
        elif isinstance(collection, LazyReference):
            raw = collection.fetch()
            return raw.to_mongo(), raw
        elif isinstance(collection, JsonSerialized):
            return collection, None
        else:
            return collection, None

    def __serialize_collection(self, collections):
        if isinstance(collections, (QuerySet, list, tuple)):
            return [self.__serialize_collection(_) for _ in collections]
        else:
            type_of_mongo, type_of_raw = self.__serialize_type_of(collections)
            return self.__filter_serialize(type_of_mongo, type_of_raw)

    @staticmethod
    def __get_raw_name(name):
        if name == "id":
            return "_id"
        else:
            return name

    def __filter_serialize(self, collections, raw):
        if isinstance(collections, dict):
            new_collection = dict()
            for index, collection in enumerate(collections.items()):
                key, value = collection
                # if no raw passed. get the raw collection in class level attribute as default value
                raw_collection = getattr(raw, self.__get_raw_name(key), self.__raw_collections)
                if isinstance(value, (list, tuple)):
                    serialized_list = list()
                    for raw_col_item in raw_collection[key]:
                        type_off_mongo, type_off_raw = self.__serialize_type_of(raw_col_item)
                        filtered = self.__filter_serialize(type_off_mongo, type_off_raw)
                        serialized_list.append(filtered)
                    new_collection.update(self.__serialize(key, serialized_list, raw_collection))
                elif isinstance(value, dict):
                    serialized_dict = self.__filter_serialize(collection, raw_collection)
                    new_collection.update(self.__serialize(key, serialized_dict, raw_collection))
                elif isinstance(value, ObjectId):
                    if "id" in collection or "_id" in collection:
                        new_key, new_value = self.__attribute_serialize(key, value)
                        new_collection.update(self.__serialize(new_key, new_value, raw_collection))
                    else:
                        # TODO:: repeat for now. will do deep serialization in the future
                        new_key, new_value = self.__attribute_serialize(key, value)
                        new_collection.update(self.__serialize(new_key, new_value, raw_collection))
                        # print(self.__serialize_collection(raw_collection))
                        # new_collection.update(self.__serialize(new_key, new_value, type_off_raw))
                else:
                    new_collection.update(self.__serialize(key, value, raw_collection))
            return new_collection
        else:
            return self.__to_string_attribute(collections)

    def __serialize(self, key, value, raw):
        serialized_attribute = self.__attribute_serialize(key, value)
        altered_serialized = self.alter_after_serialize_attributes(serialized_attribute, raw)
        new_key, new_value = altered_serialized if altered_serialized else serialized_attribute
        return JsonSerialized(**dict.fromkeys((new_key,), new_value)).to_json()

    """ 
        alter each collection before returning
    """
    def alter_after_serialize_attributes(self, serialized, raw):
        return serialized

    def alter_raw_attribute(self, raw):
        return raw

    def exclude(self, *attributes):
        self.__collections = self.__extract_list_to_exclude(self.__collections, *attributes)
        return self

    def __extract_list_to_exclude(self, items, *to_exclude):
        if isinstance(items, dict):
            _new_dict = dict()
            for item in items.items():
                k, v = item
                if isinstance(v, (list, tuple)):
                    serialized_list = self.__extract_list_to_exclude(v, *to_exclude)
                    _new_dict.update(dict.fromkeys((k,), serialized_list))
                else:
                    _new_dict.update(dict.fromkeys((k,), v))
            serialized = JsonSerialized(**_new_dict)
            serialized.exclude_attributes(*to_exclude)
            return serialized.to_json()
        if isinstance(items, (list, tuple)):
            return [self.__extract_list_to_exclude(_, *to_exclude) for _ in items]
        else:
            return items

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
        if isinstance(self.__collections, (list, tuple)):
            return [self.__dict_jsonify(_) for _ in self.__collections]
        elif isinstance(self.__collections, dict):
            return self.__dict_jsonify(self.__collections)
        else:
            return self.__dict_jsonify(self.__collections)
