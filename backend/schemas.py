from marshmallow import Schema, fields, validate

class UpdateCardSchema(Schema):
    """Schema for updating card quantities."""
    quantity_regular = fields.Integer(required=True, validate=validate.Range(min=0))
    quantity_foil = fields.Integer(required=True, validate=validate.Range(min=0))
