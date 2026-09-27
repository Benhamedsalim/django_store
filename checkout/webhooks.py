from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.http import HttpResponse
from checkout import models
from store.models import Order, Product
from django.template.loader import render_to_string
from django.core.mail import send_mail
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received


@csrf_exempt
def stripe_webhook(request):
    print('stripe webhook')
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    try:
        event = stripe.webhook.construct_event(
            payload, sig_header, settings.STRIPE_ENDPOINT_SECRET
        )
    except ValueError as e:
        print('Invalid payload')
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print('Inalid signature')
        return HttpResponse(status=400)

    # Handle the event
    if event and event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']  # contains a stripe.PaymentIntent
        print('Payment intent succeeded')
        print(payment_intent.metadata)
        transaction_id = payment_intent.metadata['transaction_id']
        make_order(transaction_id)
    else:
        # Unexpected event type
        print('Unhandled event type {}'.format(event['type']))
        return HttpResponse(status=200)

@csrf_exempt
def paypal_webhook(sender, **kwargs):
    if sender.payment_status == ST_PP_COMPLETED:
        if sender.reciver_email != settings.PAYPAL_EMAIL:
            return
        print('PaymentIntent was successful')
        make_order(sender.invoice)

valid_ipn_received.connect(paypal_webhook)


def make_order(transaction_id):
    transaction = models.Transaction.objects.get(pk=transaction_id)
    order = Order.objects.craete(transaction=transaction)
    products = Product.objects.filter(pk__in=transaction.items)
    transaction.status = models.TransactionStatus.Completed
    transaction.save()

    for product in products:
        order.orderproduct_set.create(product_id=product.id, price=product.price)

    msg_html = render_to_string('emails/order.html', {
        'order': order,
        'products': products,
    })
    send_mail(
        subject='Order Completed',
        html_message=msg_html,
        message=msg_html,
        from_email='no-replay@exampel.com',
        recipient_list=[transaction.customer.email],
        )