from django import template
from django.template.loader import get_template
from django.forms import BaseForm
from django.forms.forms import BoundField
from django.conf import settings

register = template.Library()

@register.filter
def get_form_field_type(field):
    """Returns value for the given field for a form."""
    return field.field.__class__.__name__

@register.simple_tag(takes_context=True)
def reform(context, form_or_field, layout='vertical,false'):
    """This is my rendition of the as_bootstrap filter from the 
    bootstrap_toolkit as tag because I want to take in the perms parameter
    and pass it on to the bootstrap templates for use in rendering
    fields."""
    params = layout.split(',')
    layout = str(params[0]).lower()
    try:
        bootstrap_float = str(params[1]).lower() == 'float'
    except IndexError:
        bootstrap_float = False
    context['form'] = form_or_field
    context['layout'] = layout
    context['float'] = bootstrap_float
    if isinstance(form_or_field, BaseForm):
        return get_template('bootstrap_toolkit/form.html').render(context)
    elif isinstance(form_or_field, BoundField):
        return get_template("bootstrap_toolkit/field.html").render(context)
    else:
        # Display the default
        return settings.TEMPLATE_STRING_IF_INVALID
