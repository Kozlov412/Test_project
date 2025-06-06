from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def sum_prices(services):
    """Возвращает сумму цен всех услуг"""
    if not services:
        return Decimal('0.00')
    return sum(service.price for service in services)

@register.filter
def sum_durations(services):
    """Возвращает общую длительность всех услуг в минутах"""
    if not services:
        return 0
    return sum(service.duration for service in services)