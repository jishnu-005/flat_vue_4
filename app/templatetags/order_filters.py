from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the arg"""
    return value * arg

@register.filter
def filter_status(orders, status):
    """Filter orders by status"""
    return [order for order in orders if order.status == status]

@register.filter
def filter_messages(messages, args):
    sender_type, is_read = args.split(',')
    is_read = is_read == 'True'
    return [m for m in messages if m.sender_type == sender_type and m.is_read == is_read]

@register.filter
def basename(value):
    """Returns the basename of a file path"""
    return value.split('/')[-1] if value else ''

@register.filter
def modulo(value, arg):
    """Returns the remainder of value divided by arg"""
    return value % arg