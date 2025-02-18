from django import template
from django.utils.timezone import now
import datetime



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
        # Calculate the discount percentage
        discount = ((original_price - discount_price) / original_price) * 100
        return round(discount, 2)  # Round to 2 decimal places
    except ZeroDivisionError:
        return 0  # In case the original price is zero