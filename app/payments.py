from datetime import datetime
from flask import current_app
import stripe
from .models import Payment
from . import db


stripe.api_key = current_app.config['STRIPE_SECRET_KEY']


from datetime import datetime

def create_checkout_session(amount, currency='ron', user_id=None, room_id=None, check_in_date=None, check_out_date=None):
    try:
        # Convert 'lei' to 'RON'
        if currency.lower() == 'lei':
            currency = 'ron'

        # Convert dates to datetime objects
        check_in_date = datetime.strptime(check_in_date, '%d-%m-%Y')
        check_out_date = datetime.strptime(check_out_date, '%d-%m-%Y')

        # Creare PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Amount in subdiviziunea bancnotei
            currency=currency,
        )

        # Creare CheckoutSession
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

        # Salvare detalii plată în baza de date
        payment = Payment(
            user_id=user_id,
            amount=amount,
            currency=currency,
            status='pending',
            payment_intent_id=intent.id,  # Folosim intent.id pentru payment_intent_id
            room_id=room_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date
        )
        db.session.add(payment)
        db.session.commit()

        return {
            'checkout_url': checkout_session.url,
            'client_secret': intent.client_secret,
            'payment_id': payment.id
        }

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
