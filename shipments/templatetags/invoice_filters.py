# shipments/templatetags/invoice_filters.py
from django import template

register = template.Library()

@register.filter
def sum_payments(payments):
    return sum(payment.amount for payment in payments)

@register.filter(name='sub')
def subtract(value, arg):
    return value - arg
