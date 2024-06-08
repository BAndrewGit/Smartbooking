from sqlalchemy import JSON

from . import db
from datetime import datetime, timezone
from enum import Enum


class PropertyType(Enum):
    HOTEL = "hotel"
    APARTMENT = "apartment"
    GUEST_HOUSE = "guest_house"
    BED_AND_BREAKFAST = "bed_and_breakfast"
    APARTHOTEL = "aparthotel"
    HOLIDAY_HOME = "holiday_home"
    LODGE = "lodge"
    CAMPING = "camping"
    HOMESTAY = "homestay"
    VILLA = "villa"
    COUNTRY_HOUSE = "country_house"
    RESORT = "resort"
    CHALET = "chalet"
    MOTEL = "motel"
    HOLIDAY_PARK = "holiday_park"
    CAPSULE_HOTEL = "capsule_hotel"
    INN = "inn"
    BOAT = "boat"
    FARM_HOLIDAY = "farm_holiday"
    HOSTEL = "hostel"
    CAMP = "camp"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    properties = db.relationship('Property', backref='owner', cascade='all, delete-orphan')
    reservations = db.relationship('Reservation', backref='user', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', cascade='all, delete-orphan')
    preferences = db.relationship('UserPreferences', back_populates='user', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(50))
    region = db.Column(db.String(50))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    check_in = db.Column(db.String(20))
    check_out = db.Column(db.String(20))
    num_reviews = db.Column(db.Integer)
    availability = db.Column(db.Boolean, default=True)
    stars = db.Column(db.Integer)
    type = db.Column(db.Enum(PropertyType), nullable=False)
    description = db.Column(db.Text)
    images = db.Column(JSON, nullable=True)
    cluster = db.Column(db.Integer)

    rooms = db.relationship('Room', backref='property', cascade='all, delete-orphan')
    reservations = db.relationship('Reservation', backref='property', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='property', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='property', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'name': self.name,
            'address': self.address,
            'postal_code': self.postal_code,
            'country': self.country,
            'region': self.region,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'check_in': self.check_in,
            'check_out': self.check_out,
            'num_reviews': self.num_reviews,
            'availability': self.availability,
            'stars': self.stars,
            'type': self.type.value,
            'description': self.description,
            'images': self.images,
            'cluster': self.cluster
        }


class Facility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    room_type = db.Column(db.String(50))
    persons = db.Column(db.Integer)
    price = db.Column(db.Float)
    currency = db.Column(db.String(10))
    price_rating = db.Column(db.String(20))

    reservations = db.relationship('Reservation', backref='room', cascade='all, delete-orphan')
    facilities = db.relationship('RoomFacility', backref='room', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'property_id': self.property_id,
            'room_type': self.room_type,
            'persons': self.persons,
            'price': self.price,
            'currency': self.currency,
            'price_rating': self.price_rating,
            'facilities': [facility.to_dict() for facility in self.facilities]
        }


class RoomFacility(db.Model):
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), primary_key=True)
    facility_id = db.Column(db.Integer, db.ForeignKey('facility.id'), primary_key=True)
    presence = db.Column(db.Boolean, default=True)

    facility = db.relationship('Facility', backref='room_facilities')

    def to_dict(self):
        return {
            'room_id': self.room_id,
            'facility_id': self.facility_id,
            'presence': self.presence,
            'facility_name': self.facility.name
        }


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    check_in_date = db.Column(db.DateTime, nullable=False)
    check_out_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'property_id': self.property_id,
            'room_id': self.room_id,
            'check_in_date': self.check_in_date.isoformat(),
            'check_out_date': self.check_out_date.isoformat(),
            'status': self.status
        }


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    review_text = db.Column(db.Text)
    rating_personal = db.Column(db.Float)
    rating_facilities = db.Column(db.Float)
    rating_cleanliness = db.Column(db.Float)
    rating_comfort = db.Column(db.Float)
    rating_value_for_money = db.Column(db.Float)
    rating_location = db.Column(db.Float)
    rating_wifi = db.Column(db.Float)
    review_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'property_id': self.property_id,
            'review_text': self.review_text,
            'rating_personal': self.rating_personal,
            'rating_facilities': self.rating_facilities,
            'rating_cleanliness': self.rating_cleanliness,
            'rating_comfort': self.rating_comfort,
            'rating_value_for_money': self.rating_value_for_money,
            'rating_location': self.rating_location,
            'rating_wifi': self.rating_wifi,
            'review_date': self.review_date.isoformat()
        }


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    added_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'property_id': self.property_id,
            'added_date': self.added_date.isoformat()
        }


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    payment_intent_id = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'payment_intent_id': self.payment_intent_id,
            'created_at': self.created_at.isoformat()
        }


class UserPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating_personal = db.Column(db.Float, nullable=True)
    rating_facilities = db.Column(db.Float, nullable=True)
    rating_cleanliness = db.Column(db.Float, nullable=True)
    rating_comfort = db.Column(db.Float, nullable=True)
    rating_value_for_money = db.Column(db.Float, nullable=True)
    rating_location = db.Column(db.Float, nullable=True)
    rating_wifi = db.Column(db.Float, nullable=True)

    user = db.relationship('User', back_populates='preferences')

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'rating_personal': self.rating_personal,
            'rating_facilities': self.rating_facilities,
            'rating_cleanliness': self.rating_cleanliness,
            'rating_comfort': self.rating_comfort,
            'rating_value_for_money': self.rating_value_for_money,
            'rating_location': self.rating_location,
            'rating_wifi': self.rating_wifi
        }
