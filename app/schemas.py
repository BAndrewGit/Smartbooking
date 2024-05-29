from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    created_at = fields.DateTime(dump_only=True)


class PropertySchema(Schema):
    id = fields.Int(dump_only=True)
    owner_id = fields.Int(required=True)
    name = fields.Str(required=True)
    address = fields.Str(required=True)
    postal_code = fields.Str()
    country = fields.Str()
    region = fields.Str()
    latitude = fields.Float()
    longitude = fields.Float()
    check_in = fields.Str()
    check_out = fields.Str()
    price = fields.Float(required=True)
    currency = fields.Str(required=True)
    num_reviews = fields.Int()
    availability = fields.Bool()
    stars = fields.Int()
    type = fields.Str(required=True)
    description = fields.Str()
    images = fields.Str()


class FacilitySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class RoomSchema(Schema):
    id = fields.Int(dump_only=True)
    property_id = fields.Int(required=True)
    room_type = fields.Str()
    persons = fields.Int()


class ReservationSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    property_id = fields.Int(required=True)
    check_in_date = fields
