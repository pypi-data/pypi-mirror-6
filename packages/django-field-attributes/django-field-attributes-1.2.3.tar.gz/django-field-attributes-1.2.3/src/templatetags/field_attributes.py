from string import strip
from django.template import Library

register = Library()

@register.inclusion_tag('field.html')
def field(field, *args, **kwargs):
    """
    Substitute field widget attributes
    """

    required = kwargs.get('required')

    if required in [True, 'True', 'required']:
        kwargs['required'] = 'required'

    field.field.widget.attrs.update(kwargs)
    return {'field': field}


@register.filter
def is_widget(value, arg):
    """
    Check widget class name
    """
    return value.field.widget.__class__.__name__ in map(strip, arg.split(','))
