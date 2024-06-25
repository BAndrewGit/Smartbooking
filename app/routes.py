import time
import os
import json
from datetime import datetime, timezone
from functools import wraps
import stripe
from flask import Blueprint, request, jsonify, current_app as app, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import func, and_
from werkzeug.utils import secure_filename
from .ai import recommend_properties, predict_price_for_room
from .models import User, Property, Room, Reservation, Review, Favorite, db, UserPreferences, Payment, reservation_rooms
from .payments import refund_payment, create_checkout_session, handle_payment_intent_succeeded

stripe.api_key = app.config['STRIPE_SECRET_KEY']

routes_bp = Blueprint('routes', __name__)


# Configurare pentru directorul de încărcare
UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Decorators for access control
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') not in roles:
                return jsonify({'message': 'Unauthorized'}), 403
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def check_property_owner_or_superadmin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        claims = get_jwt()
        room_id = kwargs.get('room_id')
        room = Room.query.get_or_404(room_id)
        property_item = Property.query.get_or_404(room.property_id)
        if property_item.owner_id != user_id and claims['role'] != 'superadmin':
            return jsonify({'message': 'Unauthorized'}), 403
        return f(*args, **kwargs)

    return decorated_function


def check_property_owner(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        property_id = kwargs.get('property_id') or request.json.get('property_id')
        property_item = Property.query.get_or_404(property_id)
        if property_item.owner_id != user_id:
            return jsonify({'message': 'Unauthorized'}), 403
        return f(*args, **kwargs)

    return decorated_function


def check_review_owner(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        review_id = kwargs.get('review_id')
        review = Review.query.get_or_404(review_id)
        if review.user_id != user_id:
            return jsonify({'message': 'Unauthorized'}), 403
        return f(*args, **kwargs)
    return decorated_function


def check_review_owner_or_superadmin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        claims = get_jwt()
        review_id = kwargs.get('review_id')
        review = Review.query.get_or_404(review_id)
        if review.user_id != user_id and claims['role'] != 'superadmin':
            return jsonify({'message': 'Unauthorized'}), 403
        return f(*args, **kwargs)

    return decorated_function


def check_reservation_owner_or_superadmin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        claims = get_jwt()
        reservation_id = kwargs.get('reservation_id')
        reservation = Reservation.query.get_or_404(reservation_id)
        if reservation.user_id != user_id and claims['role'] != 'superadmin':
            return jsonify({'message': 'Unauthorized'}), 403
        return f(*args, **kwargs)

    return decorated_function


# Management Admin
@routes_bp.route('/admin/users/role', methods=['PUT'])
@jwt_required()
@role_required('superadmin')
def update_user_role():
    data = request.get_json()
    username_or_email = data.get('username_or_email')
    new_role = data.get('role')
    current_user_id = get_jwt_identity()

    # Debugging logs
    app.logger.debug(f"Received data: {data}")

    user = User.query.filter((User.name == username_or_email) | (User.email == username_or_email)).first()

    # Debugging logs
    app.logger.debug(f"Queried user: {user}")

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if new_role not in ['user', 'owner', 'superadmin']:
        return jsonify({'message': 'Invalid role specified'}), 400

    # Prevenire schimbare rol propriu de la superadmin la altceva
    if user.id == current_user_id and user.role == 'superadmin' and new_role != 'superadmin':
        return jsonify({'message': 'Cannot change own role from superadmin to another role'}), 400

    user.role = new_role
    db.session.commit()

    return jsonify({'message': 'User role updated successfully'}), 200


# User Management
@routes_bp.route('/user', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@routes_bp.route('/user', methods=['PUT'])
@jwt_required()
def update_current_user():
    user_id = get_jwt_identity()
    data = request.get_json()
    user = User.query.get_or_404(user_id)
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify({'message': 'User updated successfully'}), 200


@routes_bp.route('/user', methods=['DELETE'])
@jwt_required()
def delete_current_user():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200


@routes_bp.route('/user/preferences', methods=['POST'])
@jwt_required()
def create_user_preferences():
    user_id = get_jwt_identity()
    data = request.get_json()

    total_score = sum([
        data.get('rating_personal', 0),
        data.get('rating_facilities', 0),
        data.get('rating_cleanliness', 0),
        data.get('rating_comfort', 0),
        data.get('rating_value_for_money', 0),
        data.get('rating_location', 0),
        data.get('rating_wifi', 0)
    ])

    if total_score > 44:
        return jsonify(
            {'error': f'Total score of preferences must be less than or equal to 44, yours is {total_score}'}), 400

    preferences = UserPreferences(
        user_id=user_id,
        rating_personal=data.get('rating_personal'),
        rating_facilities=data.get('rating_facilities'),
        rating_cleanliness=data.get('rating_cleanliness'),
        rating_comfort=data.get('rating_comfort'),
        rating_value_for_money=data.get('rating_value_for_money'),
        rating_location=data.get('rating_location'),
        rating_wifi=data.get('rating_wifi')
    )

    db.session.add(preferences)
    db.session.commit()

    return jsonify(preferences.to_dict()), 201


@routes_bp.route('/user/preferences', methods=['PUT'])
@jwt_required()
def update_user_preferences():
    user_id = get_jwt_identity()
    data = request.get_json()

    preferences = UserPreferences.query.filter_by(user_id=user_id).first()
    if not preferences:
        return jsonify({'error': 'Preferences not found'}), 404

    total_score = sum([
        data.get('rating_personal', preferences.rating_personal or 0),
        data.get('rating_facilities', preferences.rating_facilities or 0),
        data.get('rating_cleanliness', preferences.rating_cleanliness or 0),
        data.get('rating_comfort', preferences.rating_comfort or 0),
        data.get('rating_value_for_money', preferences.rating_value_for_money or 0),
        data.get('rating_location', preferences.rating_location or 0),
        data.get('rating_wifi', preferences.rating_wifi or 0)
    ])

    if total_score > 44:
        return jsonify(
            {'error': f'Total score of preferences must be less than or equal to 44, yours is {total_score}'}), 400

    preferences.rating_personal = data.get('rating_personal', preferences.rating_personal)
    preferences.rating_facilities = data.get('rating_facilities', preferences.rating_facilities)
    preferences.rating_cleanliness = data.get('rating_cleanliness', preferences.rating_cleanliness)
    preferences.rating_comfort = data.get('rating_comfort', preferences.rating_comfort)
    preferences.rating_value_for_money = data.get('rating_value_for_money', preferences.rating_value_for_money)
    preferences.rating_location = data.get('rating_location', preferences.rating_location)
    preferences.rating_wifi = data.get('rating_wifi', preferences.rating_wifi)

    db.session.commit()

    return jsonify(preferences.to_dict()), 200


@routes_bp.route('/user/preferences', methods=['GET'])
@jwt_required()
def get_user_preferences():
    user_id = get_jwt_identity()
    preferences = UserPreferences.query.filter_by(user_id=user_id).first()
    if not preferences:
        return jsonify({'error': 'Preferences not found'}), 404
    return jsonify(preferences.to_dict()), 200


# Property Management
@routes_bp.route('/properties', methods=['POST'])
@jwt_required()
@role_required('owner')
def create_property():
    user_id = get_jwt_identity()
    data = request.form.to_dict()

    images = request.files.getlist('images')  # Obține lista de fișiere

    image_paths = []
    for image in images:
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        image_paths.append(image_path)

    new_property = Property(
        owner_id=user_id,
        name=data['name'],
        address=data['address'],
        postal_code=data['postal_code'],
        country=data['country'],
        region=data['region'],
        latitude=float(data['latitude']),
        longitude=float(data['longitude']),
        check_in=data['check_in'],
        check_out=data['check_out'],
        num_reviews=int(data['num_reviews']),
        availability=bool(data['availability']),
        stars=int(data['stars']),
        type=data['type'],
        description=data['description'],
        images=json.dumps(image_paths)  # Salvăm ca șir JSON
    )
    db.session.add(new_property)
    db.session.commit()

    return jsonify({'message': 'Property created successfully'}), 201


@routes_bp.route('/filter_properties', methods=['GET'])
@jwt_required(optional=True)
def filter_properties():
    user_id = get_jwt_identity()
    user_preferences = UserPreferences.query.filter_by(user_id=user_id).first()

    # Verifică dacă există preferințe completate
    preferences_completed = user_preferences and all(
        value is not None for value in [
            user_preferences.rating_personal,
            user_preferences.rating_facilities,
            user_preferences.rating_cleanliness,
            user_preferences.rating_comfort,
            user_preferences.rating_value_for_money,
            user_preferences.rating_location,
            user_preferences.rating_wifi
        ]
    )

    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    num_persons = request.args.get('num_persons', type=int)
    sort_by = request.args.get('sort_by', 'default')
    price_max = request.args.get('price_max', type=float)

    if not check_in or not check_out or not num_persons:
        return jsonify({'message': 'Missing required fields: check_in, check_out, num_persons'}), 400

    region = request.args.get('region', None)
    facilities = request.args.getlist('facilities')

    try:
        check_in_date = datetime.strptime(check_in, '%d-%m-%Y')
        check_out_date = datetime.strptime(check_out, '%d-%m-%Y')
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use dd-mm-yyyy.'}), 400

    # Filtrare camere rezervate în perioada specificată
    reserved_rooms_subquery = db.session.query(reservation_rooms.c.room_id).filter(
        reservation_rooms.c.reservation_id.in_(
            db.session.query(Reservation.id).filter(
                Reservation.check_in_date < check_out_date,
                Reservation.check_out_date > check_in_date
            ).subquery()
        )
    ).subquery()

    # Filtrare proprietăți care au camere disponibile
    properties_query = db.session.query(Property).join(Room).filter(
        ~Room.id.in_(reserved_rooms_subquery)
    )

    if region:
        properties_query = properties_query.filter(Property.region == region)

    if facilities and any(facility.strip() for facility in facilities):
        for facility in facilities:
            if facility:
                properties_query = properties_query.filter(getattr(Room, facility) == True)

    available_properties = properties_query.all()

    def find_rooms_to_accommodate(property_item, num_persons):
        rooms = property_item.rooms
        selected_rooms = []
        total_persons = 0
        total_price = 0.0

        for room in sorted(rooms, key=lambda r: r.persons, reverse=True):
            selected_rooms.append(room)
            total_persons += room.persons
            total_price += room.price

            if total_persons >= num_persons:
                return selected_rooms, total_price

        return selected_rooms if total_persons >= num_persons else None, total_price

    result_properties = []
    for property_item in available_properties:
        rooms, total_price = find_rooms_to_accommodate(property_item, num_persons)
        if rooms and (price_max is None or total_price <= price_max):
            total_persons = sum(room.persons for room in rooms)
            result_properties.append({
                **property_item.to_dict(),
                'rooms': [{
                    'room_type': room.room_type,
                    'persons': room.persons,
                    'price': room.price,
                    'currency': room.currency
                } for room in rooms],
                'total_price': total_price,
                'total_persons': total_persons
            })

    def sort_key(property_item):
        if sort_by == 'price_asc':
            return property_item['total_price']  # Sortare după preț total crescător
        elif sort_by == 'price_desc':
            return -property_item['total_price']  # Sortare după preț total descrescător
        elif sort_by == 'rating_avg':
            avg_rating = (
                property_item.get('nota_personal', 0) +
                property_item.get('nota_facilităţi', 0) +
                property_item.get('nota_curăţenie', 0) +
                property_item.get('nota_confort', 0) +
                property_item.get('nota_raport_calitate/preţ', 0) +
                property_item.get('nota_locaţie', 0) +
                property_item.get('nota_wifi_gratuit', 0)
            ) / 7
            return -avg_rating if avg_rating is not None else float('inf')  # Sortare după media ratingurilor, descrescător
        else:
            return property_item['id']  # Ordinea implicită

    sorted_properties = sorted(result_properties, key=sort_key)

    if preferences_completed:
        user_ratings = {
            'nota_personal': user_preferences.rating_personal,
            'nota_facilităţi': user_preferences.rating_facilities,
            'nota_curăţenie': user_preferences.rating_cleanliness,
            'nota_confort': user_preferences.rating_comfort,
            'nota_raport_calitate/preţ': user_preferences.rating_value_for_money,
            'nota_locaţie': user_preferences.rating_location,
            'nota_wifi_gratuit': user_preferences.rating_wifi
        }

        recommendations = recommend_properties(
            user_id=user_id,
            user_ratings=user_ratings,
            max_budget=price_max,
            preferred_region=region,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            num_persons=num_persons
        )

        if isinstance(recommendations, list):
            recommendations = recommendations[:5]

        recommendation_ids = {rec['id'] for rec in recommendations}

        # Sortare cu recomandări prioritizate
        def sort_key_with_recommendations(property_item):
            if property_item['id'] in recommendation_ids:
                return (0, sort_key(property_item))  # Recomandările sunt sortate primele, cu criteriul de sortare suplimentar
            return (1, sort_key(property_item))

        sorted_properties = sorted(result_properties, key=sort_key_with_recommendations)

        return jsonify({
            'available_properties': sorted_properties,
            'recommendations': recommendations
        }), 200
    else:
        return jsonify({
            'available_properties': sorted_properties,
            'recommendations': []
        }), 200


@routes_bp.route('/properties/<int:property_id>', methods=['PUT'])
@jwt_required()
@check_property_owner
def update_property(property_id):
    user_id = get_jwt_identity()
    data = request.json  # Use request.json to read JSON data

    property_item = Property.query.get_or_404(property_id)
    if property_item.owner_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    images_to_add = request.files.getlist('images')
    images_to_remove = data.get('remove_images', [])

    # Convertim șirul de imagini la listă, dacă este cazul
    if property_item.images:
        property_item.images = json.loads(property_item.images)
    else:
        property_item.images = []

    if images_to_add:
        for image in images_to_add:
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            property_item.images.append(image_path)

    if images_to_remove:
        for image_path in images_to_remove:
            if image_path in property_item.images:
                property_item.images.remove(image_path)
                # Optional: șterge fișierul de pe disc
                if os.path.exists(image_path):
                    os.remove(image_path)

    # Convertim lista de imagini în șir JSON
    property_item.images = json.dumps(property_item.images)

    # Updating property fields with received data
    property_item.name = data.get('name', property_item.name)
    property_item.address = data.get('address', property_item.address)
    property_item.postal_code = data.get('postal_code', property_item.postal_code)
    property_item.country = data.get('country', property_item.country)
    property_item.region = data.get('region', property_item.region)
    property_item.latitude = data.get('latitude', property_item.latitude)
    property_item.longitude = data.get('longitude', property_item.longitude)
    property_item.check_in = data.get('check_in', property_item.check_in)
    property_item.check_out = data.get('check_out', property_item.check_out)
    property_item.num_reviews = data.get('num_reviews', property_item.num_reviews)
    property_item.availability = data.get('availability', property_item.availability)
    property_item.stars = data.get('stars', property_item.stars)
    property_item.type = data.get('type', property_item.type)
    property_item.description = data.get('description', property_item.description)

    db.session.commit()

    return jsonify({'message': 'Property updated successfully'}), 200


@routes_bp.route('/properties/owner', methods=['GET'])
@jwt_required()
def get_owner_properties():
    user_id = get_jwt_identity()
    claims = get_jwt()

    if claims['role'] == 'superadmin':
        properties = Property.query.all()
    else:
        properties = Property.query.filter_by(owner_id=user_id).all()

    return jsonify([property.to_dict() for property in properties]), 200


@routes_bp.route('/properties/<int:property_id>', methods=['DELETE'])
@jwt_required()
@check_property_owner_or_superadmin
def delete_property(property_id):
    user_id = get_jwt_identity()
    property_item = Property.query.get_or_404(property_id)

    if property_item.owner_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    db.session.delete(property_item)
    db.session.commit()

    return jsonify({'message': 'Property deleted successfully'}), 200


# Room Management
@routes_bp.route('/rooms', methods=['POST'])
@jwt_required()
@check_property_owner
def create_room():
    user_id = get_jwt_identity()
    data = request.get_json()

    # Verifică dacă toate datele necesare sunt furnizate
    required_fields = ['property_id', 'room_type', 'persons', 'price', 'currency']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400

    property_item = Property.query.get_or_404(data['property_id'])
    if property_item.owner_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    new_room = Room(
        property_id=data['property_id'],
        room_type=data['room_type'],
        persons=data['persons'],
        price=data['price'],
        currency=data['currency'],
        vedere_la_oras=data.get('vedere_la_oras', False),
        menaj_zilnic=data.get('menaj_zilnic', False),
        canale_prin_satelit=data.get('canale_prin_satelit', False),
        zona_de_luat_masa_in_aer_liber=data.get('zona_de_luat_masa_in_aer_liber', False),
        cada=data.get('cada', False),
        facilitati_de_calcat=data.get('facilitati_de_calcat', False),
        izolare_fonica=data.get('izolare_fonica', False),
        terasa_la_soare=data.get('terasa_la_soare', False),
        pardoseala_de_gresie_marmura=data.get('pardoseala_de_gresie_marmura', False),
        papuci_de_casa=data.get('papuci_de_casa', False),
        uscator_de_rufe=data.get('uscator_de_rufe', False),
        animale_de_companie=data.get('animale_de_companie', False),
        incalzire=data.get('incalzire', False),
        birou=data.get('birou', False),
        mobilier_exterior=data.get('mobilier_exterior', False),
        alarma_de_fum=data.get('alarma_de_fum', False),
        vedere_la_gradina=data.get('vedere_la_gradina', False),
        cuptor=data.get('cuptor', False),
        cuptor_cu_microunde=data.get('cuptor_cu_microunde', False),
        zona_de_relaxare=data.get('zona_de_relaxare', False),
        canapea=data.get('canapea', False),
        intrare_privata=data.get('intrare_privata', False),
        fier_de_calcat=data.get('fier_de_calcat', False),
        masina_de_cafea=data.get('masina_de_cafea', False),
        plita_de_gatit=data.get('plita_de_gatit', False),
        extinctoare=data.get('extinctoare', False),
        cana_fierbator=data.get('cana_fierbator', False),
        gradina=data.get('gradina', False),
        ustensile_de_bucatarie=data.get('ustensile_de_bucatarie', False),
        masina_de_spalat=data.get('masina_de_spalat', False),
        balcon=data.get('balcon', False),
        pardoseala_de_lemn_sau_parchet=data.get('pardoseala_de_lemn_sau_parchet', False),
        aparat_pentru_prepararea_de_ceai_cafea=data.get('aparat_pentru_prepararea_de_ceai_cafea', False),
        zona_de_luat_masa=data.get('zona_de_luat_masa', False),
        canale_prin_cablu=data.get('canale_prin_cablu', False),
        aer_conditionat=data.get('aer_conditionat', False),
        masa=data.get('masa', False),
        suport_de_haine=data.get('suport_de_haine', False),
        cada_sau_dus=data.get('cada_sau_dus', False),
        frigider=data.get('frigider', False),
        mic_dejun=data.get('mic_dejun', False)
    )

    db.session.add(new_room)
    db.session.commit()

    # Apelarea funcției de predicție a prețului și actualizarea ratingului
    price_prediction = predict_price_for_room(new_room.id)
    if 'error' in price_prediction:
        db.session.delete(new_room)
        db.session.commit()
        return jsonify({'error': price_prediction['error']}), 500

    db.session.commit()  # Confirmăm crearea camerei doar după obținerea ratingului

    return jsonify(new_room.to_dict()), 201



@routes_bp.route('/rooms', methods=['GET'])
def get_rooms():
    property_id = request.args.get('property_id')
    check_in_date = request.args.get('check_in_date')
    check_out_date = request.args.get('check_out_date')

    query = Room.query

    # Filtrare după property_id dacă este specificat
    if property_id:
        query = query.filter(Room.property_id == property_id)

    # Filtrare după date de check-in și check-out dacă sunt specificate
    if check_in_date and check_out_date:
        query = query.filter(
            ~Room.reservations.any(
                and_(
                    Reservation.check_in_date < check_out_date,
                    Reservation.check_out_date > check_in_date
                )
            )
        )

    rooms = query.all()
    return jsonify([room.to_dict() for room in rooms]), 200


@routes_bp.route('/rooms/<int:room_id>', methods=['GET'])
@jwt_required()
def get_room(room_id):
    room = Room.query.get_or_404(room_id)
    return jsonify(room.to_dict()), 200


@routes_bp.route('/rooms/<int:room_id>', methods=['PUT'])
@jwt_required()
def update_room(room_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    room = Room.query.get(room_id)
    if not room:
        return jsonify({'message': 'Room not found'}), 404

    property_item = Property.query.get(room.property_id)
    if not property_item:
        return jsonify({'message': 'Property associated with the room not found'}), 404

    if property_item.owner_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    # Update only the provided fields
    room.room_type = data.get('room_type', room.room_type)
    room.persons = data.get('persons', room.persons)
    room.price = data.get('price', room.price)
    room.currency = data.get('currency', room.currency)
    room.price_rating = data.get('price_rating', room.price_rating)

    room.vedere_la_oras = data.get('vedere_la_oras', room.vedere_la_oras)
    room.menaj_zilnic = data.get('menaj_zilnic', room.menaj_zilnic)
    room.canale_prin_satelit = data.get('canale_prin_satelit', room.canale_prin_satelit)
    room.zona_de_luat_masa_in_aer_liber = data.get('zona_de_luat_masa_in_aer_liber', room.zona_de_luat_masa_in_aer_liber)
    room.cada = data.get('cada', room.cada)
    room.facilitati_de_calcat = data.get('facilitati_de_calcat', room.facilitati_de_calcat)
    room.izolare_fonica = data.get('izolare_fonica', room.izolare_fonica)
    room.terasa_la_soare = data.get('terasa_la_soare', room.terasa_la_soare)
    room.pardoseala_de_gresie_marmura = data.get('pardoseala_de_gresie_marmura', room.pardoseala_de_gresie_marmura)
    room.papuci_de_casa = data.get('papuci_de_casa', room.papuci_de_casa)
    room.uscator_de_rufe = data.get('uscator_de_rufe', room.uscator_de_rufe)
    room.animale_de_companie = data.get('animale_de_companie', room.animale_de_companie)
    room.incalzire = data.get('incalzire', room.incalzire)
    room.birou = data.get('birou', room.birou)
    room.mobilier_exterior = data.get('mobilier_exterior', room.mobilier_exterior)
    room.alarma_de_fum = data.get('alarma_de_fum', room.alarma_de_fum)
    room.vedere_la_gradina = data.get('vedere_la_gradina', room.vedere_la_gradina)
    room.cuptor = data.get('cuptor', room.cuptor)
    room.cuptor_cu_microunde = data.get('cuptor_cu_microunde', room.cuptor_cu_microunde)
    room.zona_de_relaxare = data.get('zona_de_relaxare', room.zona_de_relaxare)
    room.canapea = data.get('canapea', room.canapea)
    room.intrare_privata = data.get('intrare_privata', room.intrare_privata)
    room.fier_de_calcat = data.get('fier_de_calcat', room.fier_de_calcat)
    room.masina_de_cafea = data.get('masina_de_cafea', room.masina_de_cafea)
    room.plita_de_gatit = data.get('plita_de_gatit', room.plita_de_gatit)
    room.extinctoare = data.get('extinctoare', room.extinctoare)
    room.cana_fierbator = data.get('cana_fierbator', room.cana_fierbator)
    room.gradina = data.get('gradina', room.gradina)
    room.ustensile_de_bucatarie = data.get('ustensile_de_bucatarie', room.ustensile_de_bucatarie)
    room.masina_de_spalat = data.get('masina_de_spalat', room.masina_de_spalat)
    room.balcon = data.get('balcon', room.balcon)
    room.pardoseala_de_lemn_sau_parchet = data.get('pardoseala_de_lemn_sau_parchet', room.pardoseala_de_lemn_sau_parchet)
    room.aparat_pentru_prepararea_de_ceai_cafea = data.get('aparat_pentru_prepararea_de_ceai_cafea', room.aparat_pentru_prepararea_de_ceai_cafea)
    room.zona_de_luat_masa = data.get('zona_de_luat_masa', room.zona_de_luat_masa)
    room.canale_prin_cablu = data.get('canale_prin_cablu', room.canale_prin_cablu)
    room.aer_conditionat = data.get('aer_conditionat', room.aer_conditionat)
    room.masa = data.get('masa', room.masa)
    room.suport_de_haine = data.get('suport_de_haine', room.suport_de_haine)
    room.cada_sau_dus = data.get('cada_sau_dus', room.cada_sau_dus)
    room.frigider = data.get('frigider', room.frigider)
    room.mic_dejun = data.get('mic_dejun', room.mic_dejun)

    db.session.commit()

    return jsonify(room.to_dict()), 200


@routes_bp.route('/rooms/<int:room_id>', methods=['DELETE'])
@jwt_required()
@check_property_owner_or_superadmin
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()

    return jsonify({'message': 'Room deleted successfully'}), 200


# Reservation Management
@routes_bp.route('/reservations', methods=['POST'])
@jwt_required()
def create_reservation():
    data = request.get_json()
    check_in_date = datetime.strptime(data['check_in_date'], '%d-%m-%Y')
    check_out_date = datetime.strptime(data['check_out_date'], '%d-%m-%Y')

    room_ids = data['room_ids']  # List of room IDs
    if not room_ids or not isinstance(room_ids, list):
        return jsonify({'message': 'room_ids must be a list of room IDs'}), 400

    total_amount = 0
    currency = None
    line_items = []

    for room_id in room_ids:
        # Check room availability for the specified period
        existing_reservations = Reservation.query.filter(
            Reservation.rooms.any(id=room_id),
            Reservation.check_in_date < check_out_date,
            Reservation.check_out_date > check_in_date
        ).all()

        if existing_reservations:
            return jsonify({'message': f'Room {room_id} is already reserved for the specified period'}), 400

        room = Room.query.get_or_404(room_id)
        num_nights = (check_out_date - check_in_date).days
        total_amount += room.price * num_nights

        line_items.append({
            'price_data': {
                'currency': room.currency,
                'product_data': {
                    'name': room.room_type,
                },
                'unit_amount': int(room.price * 100),  # Stripe acceptă valoarea în cenți
            },
            'quantity': num_nights,
        })

        if currency is None:
            currency = room.currency

    user_id = get_jwt_identity()
    property_id = data['property_id']  # Adăugăm referința la `property_id`

    # Creare checkout session
    payment_result = create_checkout_session(total_amount, currency, user_id, room_ids, data['check_in_date'], data['check_out_date'], property_id)
    if 'error' in payment_result:
        return jsonify({'error': payment_result['error']}), 500

    return jsonify({
        'checkout_url': payment_result['checkout_url'],
        'payment_id': payment_result['payment_id'],
        'message': 'Checkout session created successfully'
    }), 200


# Rute pentru paginile de succes și anulare
@routes_bp.route('/success.html')
def success():
    return render_template('success.html')


@routes_bp.route('/cancel.html')
def cancel():
    return render_template('cancel.html')


@routes_bp.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = app.config['STRIPE_ENDPOINT_SECRET']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle the payment_intent.succeeded event
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']  # contains a stripe.PaymentIntent

        # Retry logic to handle race condition
        for _ in range(10):  # retry up to 10 times
            payment = Payment.query.filter_by(payment_intent_id=intent['id']).first()
            if payment:
                handle_payment_intent_succeeded(intent)
                break
            time.sleep(1)  # wait 1 second before retrying

    return jsonify({'status': 'success'}), 200


@routes_bp.route('/reservations/<int:reservation_id>', methods=['GET'])
@jwt_required()
def get_reservation(reservation_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    reservation = Reservation.query.get_or_404(reservation_id)
    property_item = Property.query.get_or_404(reservation.room.property_id)

    if reservation.user_id != user_id and property_item.owner_id != user_id and claims['role'] != 'superadmin':
        return jsonify({'message': 'Unauthorized'}), 403

    return jsonify(reservation.to_dict()), 200


@routes_bp.route('/cancel_reservation/<int:reservation_id>', methods=['POST'])
@jwt_required()
@check_reservation_owner_or_superadmin
def cancel_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    user_id = get_jwt_identity()

    if reservation.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    # Verifică dacă anularea este cu cel puțin 15 de zile înainte de check-in
    if (reservation.check_in_date - datetime.utcnow()).days < 15:
        return jsonify({'message': 'Cancellation period has passed'}), 400

    # Returnează banii utilizând Stripe
    refund_result = refund_payment(reservation.payment_id)
    if 'error' in refund_result:
        return jsonify({'error': refund_result['error']}), 500

    reservation.status = 'cancelled'
    reservation.cancellation_date = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({'message': 'Reservation cancelled and payment refunded successfully'}), 200


# Review Management (User)
@routes_bp.route('/reviews', methods=['POST'])
@jwt_required()
def create_review():
    data = request.get_json()
    user_id = get_jwt_identity()
    new_review = Review(
        user_id=user_id,
        property_id=data['property_id'],
        review_text=data['review_text'],
        rating_personal=data['rating_personal'],
        rating_facilities=data['rating_facilities'],
        rating_cleanliness=data['rating_cleanliness'],
        rating_comfort=data['rating_comfort'],
        rating_value_for_money=data['rating_value_for_money'],
        rating_location=data['rating_location'],
        rating_wifi=data['rating_wifi']
    )
    db.session.add(new_review)
    db.session.commit()

    # Actualizează numărul de recenzii
    property_id = data['property_id']
    num_reviews = db.session.query(func.count(Review.id)).filter(Review.property_id == property_id).scalar()
    property_to_update = Property.query.get(property_id)
    property_to_update.num_reviews = num_reviews
    db.session.commit()

    return jsonify({'message': 'Review created successfully'}), 201


@routes_bp.route('/reviews', methods=['GET'])
def get_reviews():
    reviews = Review.query.all()
    return jsonify([review.to_dict() for review in reviews]), 200


@routes_bp.route('/reviews/<int:review_id>', methods=['GET'])
def get_review(review_id):
    review = Review.query.get_or_404(review_id)
    return jsonify(review.to_dict()), 200


@routes_bp.route('/reviews/<int:review_id>', methods=['PUT'])
@jwt_required()
@check_review_owner
def update_review(review_id):
    data = request.get_json()
    review = Review.query.get_or_404(review_id)
    review.review_text = data['review_text']
    review.rating_personal = data['rating_personal']
    review.rating_facilities = data['rating_facilities']
    review.rating_cleanliness = data['rating_cleanliness']
    review.rating_comfort = data['rating_comfort']
    review.rating_value_for_money = data['rating_value_for_money']
    review.rating_location = data['rating_location']
    review.rating_wifi = data['rating_wifi']
    db.session.commit()
    return jsonify({'message': 'Review updated successfully'}), 200


@routes_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
@check_review_owner_or_superadmin
def delete_review(review_id):
    user_id = get_jwt_identity()
    review = Review.query.get_or_404(review_id)
    if review.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    property_id = review.property_id
    db.session.delete(review)
    db.session.commit()

    # Actualizează numărul de recenzii
    num_reviews = db.session.query(func.count(Review.id)).filter(Review.property_id == property_id).scalar()
    property_to_update = Property.query.get(property_id)
    property_to_update.num_reviews = num_reviews
    db.session.commit()

    return jsonify({'message': 'Review deleted successfully'}), 200


# Favorite Management (User)
@routes_bp.route('/favorites', methods=['POST'])
@jwt_required()
def create_favorite():
    data = request.get_json()
    property_id = data.get('property_id')

    # Verifică dacă proprietatea există
    property_exists = Property.query.get(property_id)
    if not property_exists:
        return jsonify({'message': 'Property not found'}), 404

    new_favorite = Favorite(
        user_id=get_jwt_identity(),
        property_id=property_id
    )
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite created successfully'}), 201


@routes_bp.route('/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    user_id = get_jwt_identity()
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([favorite.to_dict() for favorite in favorites]), 200


@routes_bp.route('/favorites/<int:favorite_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite(favorite_id):
    user_id = get_jwt_identity()
    favorite = Favorite.query.filter_by(id=favorite_id, user_id=user_id).first()
    if not favorite:
        return jsonify({'message': 'Favorite not found'}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite deleted successfully'}), 200



