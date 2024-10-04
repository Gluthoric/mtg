from marshmallow import Schema, fields, validate

class UpdateCardSchema(Schema):
    """Schema for updating card quantities."""
    quantity_regular = fields.Integer(required=True, validate=validate.Range(min=0))
    quantity_foil = fields.Integer(required=True, validate=validate.Range(min=0))

class CardSearchSchema(Schema):
    """Schema for card search parameters."""
    name = fields.String()
    set_code = fields.String()
    rarity = fields.String()
    colors = fields.List(fields.String())
    page = fields.Integer(validate=validate.Range(min=1))
    per_page = fields.Integer(validate=validate.Range(min=1, max=100))

class SetSearchSchema(Schema):
    """Schema for set search parameters."""
    name = fields.String()
    set_types = fields.List(fields.String())
    page = fields.Integer(validate=validate.Range(min=1))
    per_page = fields.Integer(validate=validate.Range(min=1, max=100))
    sort_by = fields.String(validate=validate.OneOf(['released_at', 'name', 'collection_count', 'card_count']))
    sort_order = fields.String(validate=validate.OneOf(['asc', 'desc']))
