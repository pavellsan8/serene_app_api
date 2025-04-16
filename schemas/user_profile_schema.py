from marshmallow import fields
from store.ma import ma

class UserDataSchema(ma.Schema):
    email = fields.String(required=True, error_messages={"required": "Please provide a valid email address."})

class UserUpdateProfileSchema(ma.Schema):
    email = fields.String(required=True, error_messages={"required": "Please provide a valid email address."})
    name = fields.String(required=True, error_messages={"required": "Please provide a name."})
    phone_number = fields.String(required=True, error_messages={"required": "Please provide a phone number."})

class UserFavouriteSchema(ma.Schema):
    email = fields.String(required=True, error_messages={"required": "Please provide a valid email address."})
    item_id = fields.String(required=True, error_messages={"required": "Please provide a valid book ID."})