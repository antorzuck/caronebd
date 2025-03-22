from django import template
from django.utils.timezone import now
import datetime

from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''


@register.filter
def dict_get(dictionary, key):
    """ Custom template filter to get a value from a dictionary """
    return dictionary.get(int(key), 0)  # Convert key to int


@register.filter
def time_ago(value):
    """
    Convert a datetime object into a human-readable time difference.
    Example output: "2 days ago", "5 hours ago", "just now".
    """
    if not isinstance(value, datetime.datetime):
        return value  # Return as-is if it's not a datetime object
    
    delta = now() - value

    if delta.total_seconds() < 60:
        return "just now"
    elif delta.total_seconds() < 3600:
        minutes = int(delta.total_seconds() / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif delta.total_seconds() < 86400:
        hours = int(delta.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif delta.total_seconds() < 2592000:
        days = int(delta.total_seconds() / 86400)
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif delta.total_seconds() < 31536000:
        months = int(delta.total_seconds() / 2592000)
        return f"{months} month{'s' if months > 1 else ''} ago"
    else:
        years = int(delta.total_seconds() / 31536000)
        return f"{years} year{'s' if years > 1 else ''} ago"


@register.filter
def discount_percentage(original_price, discount_price):
    try:
        # Ensure values are Decimal
        original_price = Decimal(original_price)
        discount_price = Decimal(discount_price)

        # Prevent division by zero and invalid operations
        if original_price <= 0 or discount_price < 0:
            return 0

        discount = ((original_price - discount_price) / original_price) * 100
        return round(discount, 2)
    except (InvalidOperation, TypeError, ValueError, ZeroDivisionError):
        return 0  # Return 0 if there's any issue
@register.filter
def get_attribute_data(product_attributes_data, attr_name):
    return [data for data in product_attributes_data if data["attribute_name"] == attr_name]

@register.filter
def get_value_data(attribute_data, value):
    for data in attribute_data:
        if data["attribute_value"] == value:
            return data
    return None
