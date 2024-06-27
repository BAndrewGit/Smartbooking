from sqlalchemy import JSON, func, Table, Column, Integer, ForeignKey, LargeBinary
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.orm import relationship
from . import db
from datetime import datetime, timezone
from enum import Enum
import base64
import pickle


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


reservation_rooms = Table('reservation_rooms', db.Model.metadata,
                          Column('reservation_id', Integer, ForeignKey('reservation.id'), primary_key=True),
                          Column('room_id', Integer, ForeignKey('room.id'), primary_key=True))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
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
    num_reviews = db.Column(db.Integer, default=0)
    availability = db.Column(db.Boolean, default=True)
    stars = db.Column(db.Integer)
    type = db.Column(db.Enum(PropertyType), nullable=False)
    description = db.Column(db.Text)
    images = Column(LargeBinary)
    cluster = db.Column(db.Integer)

    rooms = db.relationship('Room', backref='property', cascade='all, delete-orphan')
    reservations = db.relationship('Reservation', backref='property', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='property', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='property', cascade='all, delete-orphan')

    def average_rating(self, attribute):
        avg = db.session.query(func.avg(getattr(Review, attribute))).filter(Review.property_id == self.id).scalar()
        return avg if avg is not None else 0

    def to_dict(self):
        image_list = []
        if self.images:
            image_bytes_list = pickle.loads(self.images)
            image_list = [base64.b64encode(img).decode('utf-8') for img in image_bytes_list]

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
            'type': self.type.value if isinstance(self.type, PropertyType) else self.type,
            'description': self.description,
            'images': image_list,
            'cluster': self.cluster,
            'nota_personal': self.average_rating('rating_personal'),
            'nota_facilităţi': self.average_rating('rating_facilities'),
            'nota_curăţenie': self.average_rating('rating_cleanliness'),
            'nota_confort': self.average_rating('rating_comfort'),
            'nota_raport_calitate_preţ': self.average_rating('rating_value_for_money'),
            'nota_locaţie': self.average_rating('rating_location'),
            'nota_wifi_gratuit': self.average_rating('rating_wifi')
        }


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    room_type = db.Column(db.String(50))
    persons = db.Column(db.Integer)
    price = db.Column(db.Float)
    currency = db.Column(db.String(10))
    price_rating = db.Column(db.String(20))

    reservations = db.relationship('Reservation', secondary=reservation_rooms, back_populates='rooms')

    vedere_la_oras = db.Column(db.Boolean, default=False)
    menaj_zilnic = db.Column(db.Boolean, default=False)
    canale_prin_satelit = db.Column(db.Boolean, default=False)
    zona_de_luat_masa_in_aer_liber = db.Column(db.Boolean, default=False)
    cada = db.Column(db.Boolean, default=False)
    facilitati_de_calcat = db.Column(db.Boolean, default=False)
    izolare_fonica = db.Column(db.Boolean, default=False)
    terasa_la_soare = db.Column(db.Boolean, default=False)
    pardoseala_de_gresie_marmura = db.Column(db.Boolean, default=False)
    papuci_de_casa = db.Column(db.Boolean, default=False)
    uscator_de_rufe = db.Column(db.Boolean, default=False)
    animale_de_companie = db.Column(db.Boolean, default=False)
    incalzire = db.Column(db.Boolean, default=False)
    birou = db.Column(db.Boolean, default=False)
    mobilier_exterior = db.Column(db.Boolean, default=False)
    alarma_de_fum = db.Column(db.Boolean, default=False)
    vedere_la_gradina = db.Column(db.Boolean, default=False)
    cuptor = db.Column(db.Boolean, default=False)
    cuptor_cu_microunde = db.Column(db.Boolean, default=False)
    zona_de_relaxare = db.Column(db.Boolean, default=False)
    canapea = db.Column(db.Boolean, default=False)
    intrare_privata = db.Column(db.Boolean, default=False)
    fier_de_calcat = db.Column(db.Boolean, default=False)
    masina_de_cafea = db.Column(db.Boolean, default=False)
    plita_de_gatit = db.Column(db.Boolean, default=False)
    extinctoare = db.Column(db.Boolean, default=False)
    cana_fierbator = db.Column(db.Boolean, default=False)
    gradina = db.Column(db.Boolean, default=False)
    ustensile_de_bucatarie = db.Column(db.Boolean, default=False)
    masina_de_spalat = db.Column(db.Boolean, default=False)
    balcon = db.Column(db.Boolean, default=False)
    pardoseala_de_lemn_sau_parchet = db.Column(db.Boolean, default=False)
    aparat_pentru_prepararea_de_ceai_cafea = db.Column(db.Boolean, default=False)
    zona_de_luat_masa = db.Column(db.Boolean, default=False)
    canale_prin_cablu = db.Column(db.Boolean, default=False)
    aer_conditionat = db.Column(db.Boolean, default=False)
    masa = db.Column(db.Boolean, default=False)
    suport_de_haine = db.Column(db.Boolean, default=False)
    cada_sau_dus = db.Column(db.Boolean, default=False)
    frigider = db.Column(db.Boolean, default=False)
    mic_dejun = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'property_id': self.property_id,
            'room_type': self.room_type,
            'persons': self.persons,
            'price': self.price,
            'currency': self.currency,
            'price_rating': self.price_rating,
            'vedere_la_oras': self.vedere_la_oras,
            'menaj_zilnic': self.menaj_zilnic,
            'canale_prin_satelit': self.canale_prin_satelit,
            'zona_de_luat_masa_in_aer_liber': self.zona_de_luat_masa_in_aer_liber,
            'cada': self.cada,
            'facilitati_de_calcat': self.facilitati_de_calcat,
            'izolare_fonica': self.izolare_fonica,
            'terasa_la_soare': self.terasa_la_soare,
            'pardoseala_de_gresie_marmura': self.pardoseala_de_gresie_marmura,
            'papuci_de_casa': self.papuci_de_casa,
            'uscator_de_rufe': self.uscator_de_rufe,
            'animale_de_companie': self.animale_de_companie,
            'incalzire': self.incalzire,
            'birou': self.birou,
            'mobilier_exterior': self.mobilier_exterior,
            'alarma_de_fum': self.alarma_de_fum,
            'vedere_la_gradina': self.vedere_la_gradina,
            'cuptor': self.cuptor,
            'cuptor_cu_microunde': self.cuptor_cu_microunde,
            'zona_de_relaxare': self.zona_de_relaxare,
            'canapea': self.canapea,
            'intrare_privata': self.intrare_privata,
            'fier_de_calcat': self.fier_de_calcat,
            'masina_de_cafea': self.masina_de_cafea,
            'plita_de_gatit': self.plita_de_gatit,
            'extinctoare': self.extinctoare,
            'cana_fierbator': self.cana_fierbator,
            'gradina': self.gradina,
            'ustensile_de_bucatarie': self.ustensile_de_bucatarie,
            'masina_de_spalat': self.masina_de_spalat,
            'balcon': self.balcon,
            'pardoseala_de_lemn_sau_parchet': self.pardoseala_de_lemn_sau_parchet,
            'aparat_pentru_prepararea_de_ceai_cafea': self.aparat_pentru_prepararea_de_ceai_cafea,
            'zona_de_luat_masa': self.zona_de_luat_masa,
            'canale_prin_cablu': self.canale_prin_cablu,
            'aer_conditionat': self.aer_conditionat,
            'masa': self.masa,
            'suport_de_haine': self.suport_de_haine,
            'cada_sau_dus': self.cada_sau_dus,
            'frigider': self.frigider,
            'mic_dejun': self.mic_dejun
        }


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    check_in_date = db.Column(db.DateTime, nullable=False)
    check_out_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20))

    rooms = db.relationship('Room', secondary=reservation_rooms, back_populates='reservations')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'property_id': self.property_id,
            'rooms': [room.to_dict() for room in self.rooms],
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
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    room_ids = db.Column(JSON, nullable=False)
    check_in_date = db.Column(db.DateTime, nullable=True)
    check_out_date = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'payment_intent_id': self.payment_intent_id,
            'created_at': self.created_at.isoformat(),
            'property_id': self.property_id,
            'room_ids': self.room_ids,
            'check_in_date': self.check_in_date.isoformat() if self.check_in_date else None,
            'check_out_date': self.check_out_date.isoformat() if self.check_out_date else None
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


class RevokedToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120), nullable=False, unique=True)

    def __init__(self, jti):
        self.jti = jti

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)