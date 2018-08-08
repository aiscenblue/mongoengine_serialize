from bson import ObjectId

from mongoengine_serialize import Serialize

collection = dict({
    "_id": ObjectId("553486125ed592a10c4e8e6b"),  # random object id
    "name": str("Jeffrey Marvin")
})

expected_collection = dict({
    "id": str(collection['_id']),
    "name": collection['name']
})

serialized_data = Serialize(collection).jsonify()


def test_equal_to_expected():
    assert serialized_data == expected_collection


def test_should_not_has__id_key():
    assert not hasattr(serialized_data, '_id')


def test_id_should_be_string():
    assert type(serialized_data['id']) is str
