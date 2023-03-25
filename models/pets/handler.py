from marshmallow import Schema, fields
import datetime as df
import uuid

class Pet(object):
    def __init__(self, name, birthdate, lastVaccination, lastVaccinationDate, category, bread, owner, isNotificationEnabled):
        self._id = uuid.uuid4()
        self.name = name
        self.birthdate = birthdate
        self.lastVaccination = lastVaccination
        self.lastVaccinationDate = lastVaccinationDate
        self.category = category
        self.bread = bread
        self.owner = owner
        self.isNotificationEnabled = isNotificationEnabled
        self.created_at = df.datetime.now()

class PetSchema(Schema):
    name = fields.Str()
    birthdate = fields.DateTime()
    lastVaccination = fields.Str()
    lastVaccinationDate = fields.DateTime()
    category = fields.Str()
    bread = fields.Str()
    owner = fields.Str()
    isNotificationEnabled = fields.Bool()
    created_at = fields.DateTime()

class Vaccine(object):
    def __init__(self, name, description, time_period):
        self._id = uuid.uuid4()
        self.name = name 
        self.description = description
        self.time_period = time_period
        self.created_at = df.datetime.now()

class VaccineSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    time_period = fields.Int()
    created_at = fields.DateTime()

class Treatment(object):
    def __init__(self, disease, treatments, source):
        self._id = uuid.uuid4()
        self.disease = disease
        self.treatments = treatments
        self.source = source
        self.created_at = df.datetime.now()

class TreatmentSchema(Schema):
    disease = fields.Str()
    treatments = fields.Str()
    source = fields.Str()
    created_at = fields.DateTime()