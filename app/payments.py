from datetime import datetime
from flask import current_app
import stripe
from .models import Payment, Reservation, Room
from . import db


stripe.api_key = current_app.config['STRIPE_SECRET_KEY']


def create_checkout_session(amount, currency='ron', user_id=None, room_id=None, check_in_date=None, check_out_date=None):
    try:
        if currency.lower() == 'lei':
            currency = 'ron'

        check_in_date = datetime.strptime(check_in_date, '%d-%m-%Y')
        check_out_date = datetime.strptime(check_out_date, '%d-%m-%Y')

        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency=currency,
        )

        payment = Payment(
            user_id=user_id,
            amount=amount,
            currency=currency,
            status='pending',
            payment_intent_id=intent.id,
            room_id=room_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date
        )
        db.session.add(payment)
        db.session.commit()

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': currency,
                        'product_data': {
                            'name': f'Rezervare cazare (Room ID: {room_id})',
                            'description': f'Check-in: {check_in_date.strftime("%d-%m-%Y")}, Check-out: {check_out_date.strftime("%d-%m-%Y")}',
                        },
                        'unit_amount': int(amount * 100),
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=current_app.config['YOUR_DOMAIN'] + '/success.html',
            cancel_url=current_app.config['YOUR_DOMAIN'] + '/cancel.html',
            metadata={
                'user_id': user_id,
                'room_id': room_id,
                'check_in_date': check_in_date.strftime('%d-%m-%Y'),
                'check_out_date': check_out_date.strftime('%d-%m-%Y')
            }
        )

        # Update payment status to succeeded in DB
        payment.status = 'succeeded'
        db.session.commit()

        # Create a new reservation
        room = Room.query.get(room_id)
        new_reservation = Reservation(
            user_id=user_id,
            property_id=room.property_id,
            room_id=room_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            status='confirmed'
        )
        db.session.add(new_reservation)
        db.session.commit()

        return {
            'checkout_url': checkout_session.url,
            'client_secret': intent.client_secret,
            'payment_id': payment.id
        }

    except Exception as e:
        return {'error': str(e)}


def handle_payment_intent_succeeded(intent):
    payment = Payment.query.get(intent['metadata']['payment_id'])

    if payment and payment.status == 'succeeded':
        try:
            new_reservation = Reservation(
                user_id=payment.user_id,
                room_id=payment.room_id,
                check_in_date=payment.check_in_date,
                check_out_date=payment.check_out_date,
                status='confirmed'
            )
            db.session.add(new_reservation)
            db.session.commit()
        except Exception:
            db.session.rollback()


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
