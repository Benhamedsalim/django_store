import stripe
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from checkout.forms import UserInfoForm, myPaypalPaymentForm
from checkout.models import Transaction, PaymentMethod
from store.models import Cart, Product, Order
from django.core.mail import send_mail
import math
from django.conf import settings
from django.utils.translation import gettext as _
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse


# Create your views here.

# def make_order(request):
#     if request.method != 'POST':
#         return redirect('store.checkout')
#
#     form = UserInfoForm(request.POST)
#
#     if form.is_valid():
#         cart = Cart.objects.filter(session=request.session.session_key).last()
#         if not cart:
#             return redirect('store.checkout')
#
#         products = Product.objects.filter(pk__in=cart.items)
#
#         total = 0
#         for item in products:
#             total += item.price
#
#         if total <= 0:
#             return redirect('store.checkout')
#
#         order = Order.objects.create(
#             customer=form.cleaned_data,
#             total=total,
#         )
#
#         for product in products:
#             order.orderproduct_set.create(
#                 product_id=product.id,
#                 price=product.price,
#             )
#         send_order_email(order, products)
#         Cart.objects.filter(session=request.session.session_key).delete()
#
#         return redirect('store.checkout_complete')
#
#     return redirect('store.checkout')

def stripe_config(request):
    return JsonResponse({
        public_key: settings.STRIPE_PUBLISHABLE_KEY,
    })

def stripe_transaction(request):
    transaction = make_transaction(request, PaymentMethod.Stripe)

    if not transaction:
        return JsonResponse({
            'message': -('Please enter a valid information.'),
        }, status=400)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    intent = stripe.PaymentIntent.create(
        amount=transaction.amount * 100,
        currency=settings.CURRENCY,
        payment_method_types=['card'],
        metadata={
            'transaction': transaction.id,
        }

    )

    return JsonResponse({
        'client_secret': intent['client_secret'],
    })
def paypal_transaction(request):
    transaction = make_transaction(request, PaymentMethod.Paypal)
    if not transaction:
        return JsonResponse({
            'message': -('Please enter a valid information.'),
        }, status=400)
    form = myPaypalPaymentForm(initial={
        'busines': settings.PAYPAL_EMAIL,
        'amount': transaction.amount,
        'invoice': transaction.id,
        'currency_code': settings.CURRENCY,
        'return_url': f'http://{request.get_host()}{reverse("store.checkout_complete")}/return',
        'cancel_url': f'http://{request.get_host()}{reverse("store.checkout")}',
        'notify_url': f'http://{request.get_host()}{reverse("checkout.paypal-webhook")}',
    })

    return HttpResponse(form.render())

def make_transaction(request, pm):

    form = UserInfoForm(request.POST)

    if form.is_valid():
        cart = Cart.objects.filter(session=request.session.session_key). last()
        products = Product.objects.filter(pk__in=cart.items)

        total = 0
        for item in products:
            total += item.price

        if total <= 0:
            return None

        return Transaction.objects.create(
            customer=form.cleaned_data,
            session=request.session.session_key,
            payment_method=pm,
            items=cart.items,
            amount=math.ceil(total),

        )

    else:
        return redirect('store.checkout')

def stripe_transaction(request):
    transactions = make_transaction(request, PaymentMethod.Stripe)

def transaction(request, pm):

    form = UserInfoForm(request.POST)

    if form.is_valid():
        cart = Cart.objects.filter(session=request.session.session_key).last()
        if not cart:
            return redirect('store.checkout')

        products = Product.objects.filter(pk__in=cart.items)

        total = 0
        for item in products:
            total += item.price

        if total <= 0:
            return None
        return Transation.objects.create(
            customer=form.cleaned_data,
            session=request.session.session_key,
            payment_method=pm,
            items=Cart.items,
            amount=math.ceil(total),
        )



    else:
        return redirect('store.checkout')


def send_order_email(order, products):
    msg_html = render_to_string('emails/order.html', {
        'order': order,
        'products': products,
    })
    send_mail(
        subject='Order Completed',
        html_message=msg_html,
        message=msg_html,
        from_email='no-replay@exampel.com',
        recipient_list=[order.customer.get('email')],
    )