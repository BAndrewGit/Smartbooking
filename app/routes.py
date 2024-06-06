from datetime import datetime, timezone
from functools import wraps
import stripe
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .ai import recommend_properties, predict_price_for_room
from .models import User, Property, Room, Reservation, Review, Favorite, db, Facility, RoomFacility, UserPreferences
from .payments import create_payment_intent, confirm_payment, refund_payment

stripe.api_key = current_app.config['STRIPE_API_KEY']

routes_bp = Blueprint('routes', __name__)


# Decorators for access control
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            claims = get_jwt()
            if claims['role'] != role:
                return jsonify({'message': 'Unauthorized'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


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


@routes_bp.route('/admin/users/<int:user_id>/role', methods=['PUT'])
@jwt_required()
@role_required('superadmin')  # Doar 'superadmin' poate modifica rolurile
def update_user_role(user_id):
    data = request.get_json()
    user = User.query.get_or_404(user_id)
    new_role = data.get('role')
    current_user_id = get_jwt_identity()

    if new_role not in ['user', 'owner', 'superadmin']:
        return jsonify({'message': 'Invalid role specified'}), 400

    # Prevenire schimbare rol propriu de la superadmin la altceva
    if user.id == current_user_id and user.role == 'superadmin' and new_role != 'superadmin':
        return jsonify({'message': 'Cannot change own role from superadmin to another role'}), 400

    user.role = new_role
    db.session.commit()

    return jsonify({'message': 'User role updated successfully'}), 200


# User Management (self)
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


# Property Management (Admin)
@routes_bp.route('/properties', methods=['POST'])
@jwt_required()
def create_property():
    user_id = get_jwt_identity()
    data = request.get_json()
    new_property = Property(
        owner_id=user_id,
        name=data['name'],
        address=data['address'],
        postal_code=data['postal_code'],
        country=data['country'],
        region=data['region'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        check_in=data['check_in'],
        check_out=data['check_out'],
        num_reviews=data['num_reviews'],
        availability=data['availability'],
        stars=data['stars'],
        type=data['type'],
        description=data['description'],
        images=data['images']
    )
    db.session.add(new_property)
    db.session.commit()

    return jsonify({'message': 'Property created successfully'}), 201


@routes_bp.route('/filter_properties', methods=['GET'])
@jwt_required()
def filter_properties():
    user_id = get_jwt_identity()
    user_preferences = UserPreferences.query.filter_by(user_id=user_id).first()

    user_ratings = {}
    if user_preferences:
        user_ratings = {
            'nota_personal': user_preferences.rating_personal,
            'nota_facilităţi': user_preferences.rating_facilities,
            'nota_curăţenie': user_preferences.rating_cleanliness,
            'nota_confort': user_preferences.rating_comfort,
            'nota_raport_calitate/preţ': user_preferences.rating_value_for_money,
            'nota_locaţie': user_preferences.rating_location,
            'nota_wifi_gratuit': user_preferences.rating_wifi
        }

    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    region = request.args.get('region', None)
    price_max = request.args.get('price_max', type=float)
    num_persons = request.args.get('num_persons', type=int)
    facilities = request.args.getlist('facilities', type=int)

    try:
        check_in_date = datetime.strptime(check_in, '%d-%m-%Y')
        check_out_date = datetime.strptime(check_out, '%d-%m-%Y')
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use dd-mm-yyyy.'}), 400

    # Filtrare camere rezervate în perioada specificată
    reserved_rooms = db.session.query(Reservation.room_id).filter(
        Reservation.check_in_date < check_out_date,
        Reservation.check_out_date > check_in_date
    ).subquery()

    # Filtrare proprietăți care au camere disponibile
    properties_query = db.session.query(Property).join(Room).filter(
        ~Room.id.in_(reserved_rooms)
    )

    if region:
        properties_query = properties_query.filter(Property.region == region)

    if price_max:
        properties_query = properties_query.filter(Room.price <= price_max)

    if num_persons:
        properties_query = properties_query.filter(Room.persons >= num_persons)

    if facilities:
        for facility in facilities:
            properties_query = properties_query.join(RoomFacility).filter(
                RoomFacility.facility_id == facility,
                RoomFacility.presence == True
            )

    available_properties = properties_query.all()
    recommendations = recommend_properties(
        user_id,
        user_ratings,
        max_budget=price_max,
        preferred_region=region
    ) if user_preferences else []

    sorted_properties = sorted(available_properties, key=lambda x: x.id not in [rec['id'] for rec in recommendations])

    return jsonify({
        'available_properties': [property_item.to_dict() for property_item in sorted_properties],
        'recommendations': recommendations
    }), 200


@routes_bp.route('/properties/<int:property_id>', methods=['PUT'])
@jwt_required()
def update_property(property_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    property_item = Property.query.get_or_404(property_id)
    if property_item.owner_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    property_item.name = data['name']
    property_item.address = data['address']
    property_item.postal_code = data['postal_code']
    property_item.country = data['country']
    property_item.region = data['region']
    property_item.latitude = data['latitude']
    property_item.longitude = data['longitude']
    property_item.check_in = data['check_in']
    property_item.check_out = data['check_out']
    property_item.num_reviews = data['num_reviews']
    property_item.availability = data['availability']
    property_item.stars = data['stars']
    property_item.type = data['type']
    property_item.description = data['description']
    property_item.images = data['images']
    db.session.commit()

    return jsonify({'message': 'Property updated successfully'}), 200


@routes_bp.route('/properties/<int:property_id>', methods=['DELETE'])
@jwt_required()
def delete_property(property_id):
    user_id = get_jwt_identity()
    property_item = Property.query.get_or_404(property_id)
    if property_item.owner_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    db.session.delete(property_item)
    db.session.commit()
    return jsonify({'message': 'Property deleted successfully'}), 200


# Room Management (Admin)
@routes_bp.route('/rooms', methods=['POST'])
@jwt_required()
def create_room():
    user_id = get_jwt_identity()
    data = request.get_json()
    property_item = Property.query.get_or_404(data['property_id'])
    if property_item.owner_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    new_room = Room(
        property_id=data['property_id'],
        room_type=data['room_type'],
        persons=data['persons'],
        price=data['price'],
        currency=data['currency']
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
@jwt_required()
def get_rooms():
    rooms = Room.query.all()
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
    room = Room.query.get_or_404(room_id)
    property_item = Property.query.get_or_404(room.property_id)
    if property_item.owner_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    room.room_type = data['room_type']
    room.persons = data['persons']
    room.price = data['price']
    room.currency = data['currency']
    db.session.commit()

    # Apelarea funcției de predicție a prețului și actualizarea ratingului
    price_prediction = predict_price_for_room(room.id)
    if 'error' in price_prediction:
        return jsonify({'error': price_prediction['error']}), 500

    db.session.commit()  # Confirmăm actualizarea camerei doar după obținerea ratingului

    return jsonify(room.to_dict()), 200


@routes_bp.route('/rooms/<int:room_id>', methods=['DELETE'])
@jwt_required()
def delete_room(room_id):
    user_id = get_jwt_identity()
    room = Room.query.get_or_404(room_id)
    property_item = Property.query.get_or_404(room.property_id)
    if property_item.owner_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    db.session.delete(room)
    db.session.commit()
    return jsonify({'message': 'Room deleted successfully'}), 200


# Room Facility Management (Admin)
@routes_bp.route('/room_facilities', methods=['POST'])
@jwt_required()
def add_facility_to_room():
    user_id = get_jwt_identity()
    data = request.get_json()
    room = Room.query.get_or_404(data['room_id'])
    property_item = Property.query.get_or_404(room.property_id)
    if property_item.owner_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    facility = RoomFacility(
        room_id=room.id,
        facility_id=data['facility_id'],
        presence=data.get('presence', True)
        )
    db.session.add(facility)
    db.session.commit()

    return jsonify({'message': 'Facility added to room successfully'}), 201


@routes_bp.route('/room_facilities/<int:room_id>', methods=['GET'])
@jwt_required()
def get_facilities_for_room(room_id):
    facilities = RoomFacility.query.filter_by(room_id=room_id).all()
    return jsonify([facility.to_dict() for facility in facilities]), 200


# Reservation Management (Admin and User)
@routes_bp.route('/reservations', methods=['POST'])
@jwt_required()
def create_reservation():
    data = request.get_json()
    check_in_date = datetime.strptime(data['check_in_date'], '%d-%m-%Y')
    check_out_date = datetime.strptime(data['check_out_date'], '%d-%m-%Y')

    # Verifica disponibilitatea camerei pentru perioada specificată
    existing_reservations = Reservation.query.filter(
        Reservation.room_id == data['room_id'],
        Reservation.check_in_date < check_out_date,
        Reservation.check_out_date > check_in_date
    ).all()

    if existing_reservations:
        return jsonify({'message': 'Room is already reserved for the specified period'}), 400

    room = Room.query.get_or_404(data['room_id'])
    num_nights = (check_out_date - check_in_date).days
    amount = room.price * num_nights
    user_id = get_jwt_identity()

    # Crearea intenției de plată
    payment_result = create_payment_intent(amount, room.currency, user_id)
    if 'error' in payment_result:
        return jsonify({'error': payment_result['error']}), 500

    return jsonify({
        'client_secret': payment_result['client_secret'],
        'payment_id': payment_result['payment_id'],
        'message': 'Payment initiated successfully'
    }), 200


@routes_bp.route('/confirm_reservation', methods=['POST'])
@jwt_required()
def confirm_reservation():
    data = request.get_json()
    payment_id = data.get('payment_id')

    # Confirmarea plății
    payment_result = confirm_payment(payment_id)
    if 'error' in payment_result:
        return jsonify({'error': payment_result['error']}), 500

    # Crearea rezervării doar după confirmarea plății
    new_reservation = Reservation(
        user_id=get_jwt_identity(),
        room_id=data['room_id'],
        check_in_date=datetime.strptime(data['check_in_date'], '%d-%m-%Y'),
        check_out_date=datetime.strptime(data['check_out_date'], '%d-%m-%Y'),
        status='confirmed'
    )
    db.session.add(new_reservation)
    db.session.commit()
    return jsonify({'message': 'Reservation created and payment confirmed successfully'}), 201


@routes_bp.route('/reservations', methods=['GET'])
@jwt_required()
def get_reservations():
    user_id = get_jwt_identity()
    reservations = Reservation.query.filter_by(user_id=user_id).all()
    return jsonify([reservation.to_dict() for reservation in reservations]), 200


@routes_bp.route('/reservations/<int:reservation_id>', methods=['GET'])
@jwt_required()
def get_reservation(reservation_id):
    user_id = get_jwt_identity()
    reservation = Reservation.query.get_or_404(reservation_id)
    property_item = Property.query.get_or_404(reservation.room.property_id)
    if reservation.user_id != user_id and property_item.owner_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    return jsonify(reservation.to_dict()), 200


def cancel_reservation():
    data = request.get_json()
    reservation_id = data.get('reservation_id')
    reservation = Reservation.query.get_or_404(reservation_id)
    user_id = get_jwt_identity()

    if reservation.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    # Verifică dacă anularea este cu cel puțin 30 de zile înainte de check-in
    if (reservation.check_in_date - datetime.now(timezone.utc)).days < 30:
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
    new_review = Review(
        user_id=get_jwt_identity(),
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
def update_review(review_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    review = Review.query.get_or_404(review_id)
    if review.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403
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
def delete_review(review_id):
    user_id = get_jwt_identity()
    review = Review.query.get_or_404(review_id)
    if review.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': 'Review deleted successfully'}), 200


# Favorite Management (User)
@routes_bp.route('/favorites', methods=['POST'])
@jwt_required()
def create_favorite():
    data = request.get_json()
    new_favorite = Favorite(
        user_id=get_jwt_identity(),
        property_id=data['property_id']
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
    favorite = Favorite.query.get_or_404(favorite_id)
    if favorite.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite deleted successfully'}), 200


# Facility Management (Admin)
@routes_bp.route('/facilities', methods=['GET'])
def get_facilities():
    facilities = Facility.query.all()
    return jsonify([facility.to_dict() for facility in facilities]), 200


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
        return jsonify({'error': f'Total score of preferences must be less than or equal to 44, yours is {total_score}'}), 400

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
        return jsonify({'error': f'Total score of preferences must be less than or equal to 44, yours is {total_score}'}), 400

    preferences.rating_personal = data.get('rating_personal', preferences.rating_personal)
    preferences.rating_facilities = data.get('rating_facilities', preferences.rating_facilities)
    preferences.rating_cleanliness = data.get('rating_cleanliness', preferences.rating_cleanliness)
    preferences.rating_comfort = data.get('rating_comfort', preferences.rating_comfort)
    preferences.rating_value_for_money = data.get('rating_value_for_money', preferences.rating_value_for_money)
    preferences.rating_location = data.get('rating_location', preferences.rating_location)
    preferences.rating_wifi = data.get('rating_wifi', preferences.rating_wifi)

    db.session.commit()

    return jsonify(preferences.to_dict()), 200
