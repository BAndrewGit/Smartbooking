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
    currency = data.get('currency', 'usd')
    user_id = get_jwt_identity()

    if not amount:
        return jsonify({'error': 'Missing amount'}), 400

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Amount in cents
            currency=currency,
        )

        payment = Payment(
            user_id=user_id,
            amount=amount,
            currency=currency,
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


@payments_bp.route('/confirm_payment', methods=['POST'])
@jwt_required()
def confirm_payment():
    data = request.get_json()
    payment = Payment.query.get_or_404(data['payment_id'])

    try:
        intent = stripe.PaymentIntent.retrieve(payment.payment_intent_id)
        if intent.status == 'succeeded':
            payment.status = 'succeeded'
            db.session.commit()
            return jsonify({'message': 'Payment confirmed successfully'}), 200
        else:
            return jsonify({'message': 'Payment not confirmed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
