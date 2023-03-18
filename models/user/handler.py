from marshmallow import Schema, fields
import datetime as dt
import uuid

class User(object):
    def __init__(self, name, email, provider, image_url):
        self._id = uuid.uuid4()
        self.name = name
        self.email = email
        self.provider = provider
        self.image_url = image_url
        self.created_at = dt.datetime.now()

    def __repr__(self):
        return '<User(name={self.name!r})>'.format(self=self)

class UserSchema(Schema):
    name = fields.Str()
    provider = fields.Str()
    image_url = fields.Str()
    email = fields.Email()
    created_at = fields.Date()
    type = fields.Str()        