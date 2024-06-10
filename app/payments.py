from flask import current_app
import stripe
from .models import Payment
from . import db


stripe.api_key = current_app.config['STRIPE_API_KEY']


def create_payment_intent(amount, currency='ron', user_id=None):
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Amount in subdiviziunea bancnotei
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

        return {
            'client_secret': intent.client_secret,
            'payment_id': payment.id
        }
    except Exception as e:
        return {'error': str(e)}


def confirm_payment(payment_id):
    try:
        payment = Payment.query.get_or_404(payment_id)
        intent = stripe.PaymentIntent.retrieve(payment.payment_intent_id)
        if intent.status == 'succeeded':
            payment.status = 'succeeded'
            db.session.commit()
            return {'message': 'Payment confirmed successfully'}
        else:
            return {'error': 'Payment not confirmed'}
    except Exception as e:
        return {'error': str(e)}


def refund_payment(payment_id):
    try:
        payment = Payment.query.get_or_404(payment_id)
        if payment.status == 'succeeded':
            refund = stripe.Refund.create(
                payment_intent=payment.payment_intent_id
            )
            if refund.status == 'succeeded':
                payment.status = 'refunded'
                db.session.commit()
                return {'message': 'Payment refunded successfully'}
            else:
                return {'error': 'Refund failed'}
        else:
            return {'error': 'No valid payment found for refund'}
    except Exception as e:
        return {'error': str(e)}
