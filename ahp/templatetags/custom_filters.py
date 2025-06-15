from django import template
from fractions import Fraction
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def decimal_to_fraction(value):
    try:
        return str(Fraction(value).limit_denominator())  # Convert decimal to fraction
    except ZeroDivisionError:
        return value

@register.filter
def getattr_dynamic(value, attr_name):
    # Periksa jika value adalah dictionary
    if isinstance(value, dict):
        return value.get(attr_name, None)
    try:
        return getattr(value, attr_name, None)  # Mengakses atribut pada objek
    except AttributeError:
        return None

@register.filter
def intdot(value):
    """Mengganti pemisah ribuan koma dengan titik"""
    try:
        value = int(value)
        return "{:,}".format(value).replace(",", ".")
    except (ValueError, TypeError):
        return value