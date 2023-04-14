from marshmallow import Schema, fields, post_load

class ProfileSchema(Schema):
    name = fields.Str()

class ContactSchema(Schema):
    profile = fields.Nested(ProfileSchema)
    wa_id = fields.Str()

class MetadataSchema(Schema):
    display_phone_number = fields.Str()
    phone_number_id = fields.Str()

class MessageSchema(Schema):
    from_ = fields.Str(data_key="from")
    id_ = fields.Str(data_key="id")
    timestamp = fields.Str()
    text = fields.Dict()
    type_ = fields.Str(data_key="type")

class ChangeSchema(Schema):
    value = fields.Dict()
    field = fields.Str()
    contacts = fields.List(fields.Nested(ContactSchema))
    messages = fields.List(fields.Nested(MessageSchema))
    messaging_product = fields.Str(data_key="messaging_product")
    metadata = fields.Nested(MetadataSchema)

class EntrySchema(Schema):
    id_ = fields.Str(data_key="id")
    changes = fields.List(fields.Nested(ChangeSchema))

class WhatsAppPayloadSchema(Schema):
    object_ = fields.Str(data_key="object")
    entry = fields.List(fields.Nested(EntrySchema))

    @post_load
    def make_payload(self, data, **kwargs):
        return WhatsAppPayload(**data)

class WhatsAppPayload:
    def __init__(self, object_, entry):
        self.object = object_
        self.entry = entry