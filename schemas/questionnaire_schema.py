from marshmallow import fields
from store.ma import ma

class UserQuestionnaireAnswerSchema(ma.Schema):
    email = fields.String(required=True, error_messages={"required": "Please provide a valid email address."})
    feeling = fields.Integer(required=True, error_messages={"required": "Please select a feeling."})
    mood = fields.String(required=True, error_messages={"required": "Please select an emotion."})
    emotion = fields.List(fields.String(), required=True, error_messages={"required": "Please select at least one mood."})