from marshmallow import Schema, fields
import datetime as dt

class AuthRequestSchema(Schema):
    username = fields.Email()
    password = fields.Str()
    type = fields.Str()

class AuthResponseSchema(Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()
    created_at = fields.Date()
    type = fields.Str()

class AuthRejectSchema(Schema):
    description = fields.Email()
    status_code = fields.Int()
    type = fields.Str()

class AuthRefreshRequestSchema(Schema):
    refresh_token = fields.Str()
    type = fields.Str()

class AuthRefreshRequest(object):
    def __init__(self, refresh_token):
        self.refresh_token = refresh_token
    
    def __repr__(self):
        return '<AuthRefreshRequest(refresh_token={self.refresh_token!r})>'.format(self=self)

class AuthRequest(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def __repr__(self):
        return '<AuthRequest(username={self.username!r})>'.format(self=self)

class AuthResponse(object):
    def __init__(self, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.created_at = dt.datetime.now()
    
    def __repr__(self):
        return '<AuthResponse(access_token={self.access_token!r})>'.format(self=self)

class AuthReject(object):
    def __init__(self, description):
        self.description = description
        self.status_code = 403
    
    def __repr__(self):
        return '<AuthReject(description={self.description!r})>'.format(self=self)