# mongoengine_serializer
serialize mongoengine documents

### Current Support
serialize ObjectIds and datetime format
> if you want to improve just create a pull 
> request or put a suggestion comment inside 
> issues tab

## Installation
```
pip install mongoengine-serialize
```

# Example:

#### Your mongoengine schema
```
class Users(Document):
    avatar_url = URLField(required=True)
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    email = StringField(required=True)
    password = StringField(required=True)
    created_at = DateTimeField(default=utc_now)
```

#### Create a Users serializer that extends Serialize class from payload_serializer

```
from payload_serializer import Serialize

user = Users.objects(first_name='Hello').first()
serialized_user = Serialize(user).to_json()
```

#### Changing data attributes
> Alter data by using set_attributes function
```
UserSerializer(Serialize):

     def set_attributes(self, data):
        super().set_attributes(data)
        data['avatar_url'] = "http://" + data['avatar_ur']



user = Users.objects(first_name='Hello').first()
serialized_user = UserSerializer(user).to_json()

```

#### Exclude attributes
> exclude_attribute is called before set_attributes
> it helps on filtering your dictionary before returning
```
Serialize(user).exclude_attributes('password', 'created_at').to_json()
```
