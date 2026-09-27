from django import template

register = template.Library()

def currency(price):
    return '{:,.2f}'.format(price) + ' USD'

register.filter('currency', currency)