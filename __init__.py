from mongoengine.base import BaseDocument
from bson.objectid import ObjectId
from datetime import datetime


class Serialize:
    def __init__(self, data):
        self.set_attributes(data)

    def __call__(self, data):
        self.set_attributes(data)
        return self

    def exclude_attributes(self, *attributes):
        for attribute in attributes:
            if hasattr(self, attribute):
                delattr(self, attribute)
        return self

    @staticmethod
    def __doc_to_mongo(doc):
        if isinstance(doc, BaseDocument):
            return doc.to_mongo()
        else:
            return doc

    @staticmethod
    def __entity_to_string(key, val):
        if isinstance(val, ObjectId):
            return "id", str(val)
        elif isinstance(val, datetime):
            return key, str(val)
        else:
            return key, val

    def set_attributes(self, data):
        self.__serialize(data)

    def __serialize(self, data):
        doc_mongo = self.__doc_to_mongo(data)
        if isinstance(doc_mongo, dict):
            for key, value in doc_mongo.items():
                new_key, new_value = self.__entity_to_string(key, value)
                setattr(self, new_key, new_value)
            return self.to_json()
        else:
            raise ValueError('Cannot serialize object.')

    def to_json(self):
        return self.__dict__
