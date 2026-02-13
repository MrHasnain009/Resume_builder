from django import template

register = template.Library()

@register.filter
def split(value, key):
    """Splits a string by a given key."""
    if isinstance(value, str):
        return value.split(key)
    return value # Return original value if not a string

@register.filter
def trim(value):
    """Strips leading/trailing whitespace from a string."""
    if isinstance(value, str):
        return value.strip()
    return value # Return original value if not a string