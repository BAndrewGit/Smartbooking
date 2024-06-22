from marshmallow import Schema, fields, EXCLUDE


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    role = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True, format='%d-%m-%Y')
    properties = fields.List(fields.Nested(lambda: PropertySchema(exclude=('owner',))))
    reservations = fields.List(fields.Nested(lambda: ReservationSchema(exclude=('user',))))
    reviews = fields.List(fields.Nested(lambda: ReviewSchema(exclude=('user',))))
    favorites = fields.List(fields.Nested(lambda: FavoriteSchema(exclude=('user',))))
    preferences = fields.Nested(lambda: UserPreferencesSchema(exclude=('user',)), dump_only=True)

    class Meta:
        unknown = EXCLUDE


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
    num_reviews = fields.Int()
    availability = fields.Bool()
    stars = fields.Int()
    type = fields.Str(required=True)
    description = fields.Str()
    images = fields.List(fields.Str())
    cluster = fields.Int()
    rooms = fields.List(fields.Nested(lambda: RoomSchema(exclude=('property',))))
    reservations = fields.List(fields.Nested(lambda: ReservationSchema(exclude=('property',))))
    reviews = fields.List(fields.Nested(lambda: ReviewSchema(exclude=('property',))))
    favorites = fields.List(fields.Nested(lambda: FavoriteSchema(exclude=('property',))))

    class Meta:
        unknown = EXCLUDE


class ReservationSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    property_id = fields.Int(required=True)
    check_in_date = fields.DateTime(required=True, format='%d-%m-%Y')
    check_out_date = fields.DateTime(required=True, format='%d-%m-%Y')
    status = fields.Str(required=True)
    user = fields.Nested(lambda: UserSchema(only=('id', 'name', 'email')))
    rooms = fields.List(fields.Nested(lambda: RoomSchema(only=('id', 'room_type', 'persons', 'price', 'currency'))))
    property = fields.Nested(lambda: PropertySchema(only=('id', 'name', 'address')))

    class Meta:
        unknown = EXCLUDE


class RoomSchema(Schema):
    id = fields.Int(dump_only=True)
    property_id = fields.Int(required=True)
    room_type = fields.Str()
    persons = fields.Int()
    price = fields.Float(required=True)
    currency = fields.Str(required=True)
    price_rating = fields.Str()
    reservations = fields.List(fields.Nested(ReservationSchema, exclude=('room',)))

    vedere_la_oras = fields.Bool()
    menaj_zilnic = fields.Bool()
    canale_prin_satelit = fields.Bool()
    zona_de_luat_masa_in_aer_liber = fields.Bool()
    cada = fields.Bool()
    facilitati_de_calcat = fields.Bool()
    izolare_fonica = fields.Bool()
    terasa_la_soare = fields.Bool()
    pardoseala_de_gresie_marmura = fields.Bool()
    papuci_de_casa = fields.Bool()
    uscator_de_rufe = fields.Bool()
    animale_de_companie = fields.Bool()
    incalzire = fields.Bool()
    birou = fields.Bool()
    mobilier_exterior = fields.Bool()
    alarma_de_fum = fields.Bool()
    vedere_la_gradina = fields.Bool()
    cuptor = fields.Bool()
    cuptor_cu_microunde = fields.Bool()
    zona_de_relaxare = fields.Bool()
    canapea = fields.Bool()
    intrare_privata = fields.Bool()
    fier_de_calcat = fields.Bool()
    masina_de_cafea = fields.Bool()
    plita_de_gatit = fields.Bool()
    extinctoare = fields.Bool()
    cana_fierbator = fields.Bool()
    gradina = fields.Bool()
    ustensile_de_bucatarie = fields.Bool()
    masina_de_spalat = fields.Bool()
    balcon = fields.Bool()
    pardoseala_de_lemn_sau_parchet = fields.Bool()
    aparat_pentru_prepararea_de_ceai_cafea = fields.Bool()
    zona_de_luat_masa = fields.Bool()
    canale_prin_cablu = fields.Bool()
    aer_conditionat = fields.Bool()
    masa = fields.Bool()
    suport_de_haine = fields.Bool()
    cada_sau_dus = fields.Bool()
    frigider = fields.Bool()
    mic_dejun = fields.Bool()

    class Meta:
        unknown = EXCLUDE


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
    review_date = fields.DateTime(dump_only=True, format='%d-%m-%Y')
    user = fields.Nested(lambda: UserSchema(only=('id', 'name', 'email')))
    property = fields.Nested(lambda: PropertySchema(only=('id', 'name', 'address')))

    class Meta:
        unknown = EXCLUDE


class FavoriteSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    property_id = fields.Int(required=True)
    added_date = fields.DateTime(dump_only=True)
    user = fields.Nested(lambda: UserSchema(only=('id', 'name', 'email')))
    property = fields.Nested(lambda: PropertySchema(only=('id', 'name', 'address')))

    class Meta:
        unknown = EXCLUDE


class PaymentSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    amount = fields.Float(required=True)
    currency = fields.Str(required=True)
    status = fields.Str(required=True)
    payment_intent_id = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    property_id = fields.Int(required=True)
    room_ids = fields.List(fields.Int(), required=True)
    check_in_date = fields.DateTime(required=True, format='%d-%m-%Y')
    check_out_date = fields.DateTime(required=True, format='%d-%m-%Y')

    user = fields.Nested(lambda: UserSchema(only=('id', 'name', 'email')))
    rooms = fields.List(fields.Nested(RoomSchema, only=('id', 'room_type', 'persons', 'price', 'currency')))

    class Meta:
        unknown = EXCLUDE


class UserPreferencesSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    rating_personal = fields.Float(allow_none=True)
    rating_facilities = fields.Float(allow_none=True)
    rating_cleanliness = fields.Float(allow_none=True)
    rating_comfort = fields.Float(allow_none=True)
    rating_value_for_money = fields.Float(allow_none=True)
    rating_location = fields.Float(allow_none=True)
    rating_wifi = fields.Float(allow_none=True)

    class Meta:
        unknown = EXCLUDE


class RevokedTokenSchema(Schema):
    id = fields.Int(dump_only=True)
    jti = fields.Str(required=True)

    class Meta:
        unknown = EXCLUDE
