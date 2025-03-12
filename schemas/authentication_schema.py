from marshmallow import fields
from store.ma import ma

class UserRegisterSchema(ma.Schema):
    name = fields.String(required=True, allow_none=False, error_messages={"required": "Please provide a valid name."})
    email = fields.String(required=True, allow_none=False, error_messages={"required": "Please provide a valid email address."})
    password = fields.String(required=True, allow_none=False, error_messages={"required": "Please provide a valid password"}) 

class UserLoginSchema(ma.Schema):
    email = fields.String(required=True, allow_none=False, error_messages={"required": "Please provide a valid email address."})
    password = fields.String(required=True, allow_none=False, error_messages={"required": "Please provide a valid password"}) 

class GetEmailDataSchema(ma.Schema):
    email = fields.String(required=True, error_messages={"required": "Please provide a valid email address."})