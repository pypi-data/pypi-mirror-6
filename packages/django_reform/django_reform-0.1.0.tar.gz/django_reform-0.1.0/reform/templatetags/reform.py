from django import template


register = template.Library()

@register.filter
def get_form_field_type(field):
    """Returns value for the given field for a form."""
    return field.field.__class__.__name__
