from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import stripe
from .models import Payment
from . import db
from .schemas import PaymentSchema

stripe.api_key = current_app.config['STRIPE_API_KEY']

payments_bp = Blueprint('payments', __name__)


@payments_bp.route('/create_payment_intent', methods=['POST'])
@jwt_required()
def create_payment_intent():
    data = request.get_json()
    amount = data.get('amount')
    user_id = get_jwt_identity()

    if not amount:
        return jsonify({'error': 'Missing amount'}), 400

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Amount in bani (subdiviziunea leului)
            currency='ron',
        )

        payment = Payment(
            user_id=user_id,
            amount=amount,
            currency='ron',
            status='pending',
            payment_intent_id=intent.id
        )
        db.session.add(payment)
        db.session.commit()

        payment_schema = PaymentSchema()
        return jsonify({
            'client_secret': intent.client_secret,
            'payment': payment_schema.dump(payment)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
