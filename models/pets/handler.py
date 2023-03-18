from marshmallow import Schema, fields
import datetime as df
import uuid

class Pet(object):
    def __init__(self, name, birthdate, lastVaccination, lastVaccinationDate, category, bread, owner):
        self._id = uuid.uuid4()
        self.name = name
        self.birthdate = birthdate
        self.lastVaccination = lastVaccination
        self.lastVaccinationDate = lastVaccinationDate
        self.category = category
        self.bread = bread
        self.owner = owner
        self.created_at = df.datetime.now()

class PetSchema(Schema):
    name = fields.Str()
    birthdate = fields.DateTime()
    lastVaccination = fields.Str()
    lastVaccinationDate = fields.DateTime()
    category = fields.Str()
    bread = fields.Str()
    owner = fields.Str()
    created_at = fields.DateTime()

class VaccineEmailSchema(Schema):
    owner = fields.Str()
    email = fields.Email()
    pet = fields.Str()
    owner = fields.Str()
    vaccine = fields.Str()
    date = fields.DateTime()