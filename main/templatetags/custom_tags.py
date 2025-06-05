from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def index(value, i):
    try:
        return value[int(i)]
    except (IndexError, ValueError, TypeError):
        return ''