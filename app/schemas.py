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
    room_id = fields.Int(required=True)
    check_in_date = fields.DateTime(required=True)
    check_out_date = fields.DateTime(required=True)
    status = fields.Str(required=True)


class ReviewSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    property_id = fields.Int(required=True)
    review_text = fields.Str(required=True)
    rating_personal = fields.Float()
    rating_facilities = fields.Float()
    rating_cleanliness = fields.Float()
    rating_comfort = fields.Float()
    rating_value_for_money = fields.Float()
    rating_location = fields.Float()
    rating_wifi = fields.Float()
    review_date = fields.DateTime(dump_only=True)


class FavoriteSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    property_id = fields.Int(required=True)
    added_date = fields.DateTime(dump_only=True)


class PaymentSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    amount = fields.Float(required=True)
    currency = fields.Str(required=True)
    status = fields.Str(required=True)
    payment_intent_id = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
