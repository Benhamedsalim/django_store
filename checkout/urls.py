from django.urls import path
from . import views
from checkout import webhooks
from paypal.standard.api.views import ipn
urlpatterns = [
    #path('orders', views.make_order, name='checkout.order'),
    path('stripe', views.stripe_transaction, name='checkout.stripe'),
    path('paypal', views.paypal_transaction, name='checkout.paypal'),
    path('stripe/config', views.stripe_config, name='checkout.stripe_config'),
    path('stripe/web_hook', webhooks.stripe_webhook),
    path('paypal/webhook', ipn, name='checkout.paypal-webhook'),

]
