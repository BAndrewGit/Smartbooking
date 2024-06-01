from flask import Blueprint, request, jsonify
from .models import User, Property, Room, Reservation, Review, Favorite, db, PropertyFacility
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from functools import wraps

routes_bp = Blueprint('routes', __name__)


# Decorators for access control
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
        price=data['price'],
        currency=data['currency'],
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


@routes_bp.route('/properties', methods=['GET'])
@jwt_required()
def get_properties():
    properties = Property.query.all()
    return jsonify([property_item.to_dict() for property_item in properties]), 200


@routes_bp.route('/filter_properties', methods=['GET'])
def filter_properties():
    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    region = request.args.get('region', None)
    price_max = request.args.get('price_max', None)
    facilities = request.args.getlist('facilities', type=int)

    try:
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    # Filtram camerele rezervate în perioada specificată
    reserved_rooms = db.session.query(Reservation.room_id).filter(
        Reservation.check_in_date < check_out_date,
        Reservation.check_out_date > check_in_date
    ).subquery()

    # Filtram proprietățile care au camere disponibile
    properties_query = db.session.query(Property).join(Room).filter(
        ~Room.id.in_(reserved_rooms)
    )

    if region:
        properties_query = properties_query.filter(Property.region == region)

    if price_max:
        properties_query = properties_query.filter(Property.price <= price_max)

    if facilities:
        for facility in facilities:
            properties_query = properties_query.join(PropertyFacility).filter(
                PropertyFacility.facility_id == facility,
                PropertyFacility.presence == True
            )

    available_properties = properties_query.all()

    return jsonify([property_item.to_dict() for property_item in available_properties]), 200


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
    property_item.price = data['price']
    property_item.currency = data['currency']
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
        persons=data['persons']
    )
    db.session.add(new_room)
    db.session.commit()
    return jsonify({'message': 'Room created successfully'}), 201


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
    db.session.commit()
    return jsonify({'message': 'Room updated successfully'}), 200


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


# Reservation Management (Admin and User)
@routes_bp.route('/reservations', methods=['POST'])
@jwt_required()
def create_reservation():
    data = request.get_json()
    # Verifica disponibilitatea camerei pentru perioada specificata
    existing_reservations = Reservation.query.filter(
        Reservation.room_id == data['room_id'],
        Reservation.check_in_date < data['check_out_date'],
        Reservation.check_out_date > data['check_in_date']
    ).all()

    if existing_reservations:
        return jsonify({'message': 'Room is already reserved for the specified period'}), 400

    new_reservation = Reservation(
        user_id=get_jwt_identity(),
        room_id=data['room_id'],
        check_in_date=data['check_in_date'],
        check_out_date=data['check_out_date'],
        status=data['status']
    )
    db.session.add(new_reservation)
    db.session.commit()
    return jsonify({'message': 'Reservation created successfully'}), 201


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


@routes_bp.route('/reservations/<int:reservation_id>', methods=['PUT'])
@jwt_required()
def update_reservation(reservation_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    reservation.check_in_date = data['check_in_date']
    reservation.check_out_date = data['check_out_date']
    reservation.status = data['status']
    db.session.commit()
    return jsonify({'message': 'Reservation updated successfully'}), 200


@routes_bp.route('/reservations/<int:reservation_id>', methods=['DELETE'])
@jwt_required()
def delete_reservation(reservation_id):
    user_id = get_jwt_identity()
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    db.session.delete(reservation)
    db.session.commit()
    return jsonify({'message': 'Reservation deleted successfully'}), 200


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
@jwt_required()
def get_reviews():
    reviews = Review.query.all()
    return jsonify([review.to_dict() for review in reviews]), 200


@routes_bp.route('/reviews/<int:review_id>', methods=['GET'])
@jwt_required()
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
