from django import template

register = template.Library()

@register.filter
def js_date(value):
    return value.strftime("%Y-%m-%d")