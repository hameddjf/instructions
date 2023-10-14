from django import template

register = template.Library()


@register.filter
def translate_numbers(value):
    value = str(value)
    E2P_tbl = value.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
    return value.translate(E2P_tbl)
