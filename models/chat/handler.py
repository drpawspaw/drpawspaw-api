from marshmallow import Schema, fields

class ChatSchema(Schema):
    message = fields.Str()
    session = fields.Str()