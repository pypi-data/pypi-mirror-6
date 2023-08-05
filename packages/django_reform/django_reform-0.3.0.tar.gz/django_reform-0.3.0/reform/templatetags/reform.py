from django import template
from django.template.loader import get_template
import itertools


register = template.Library()

def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.izip_longest(fillvalue=fillvalue, *args)

@register.filter
def get_form_field_type(field):
    """Returns value for the given field for a form."""
    return field.field.__class__.__name__

@register.simple_tag(takes_context=True)
def reform(context, form, include=None, layout='vertical,false,1'):
    """This is my rendition of the as_bootstrap filter from the 
    bootstrap_toolkit as tag because I want to take in the perms parameter
    and pass it on to the bootstrap templates for use in rendering
    fields."""
    params = [param.strip() for param in layout.split(',')]
    layout = str(params[0]).lower()
    columns = int(params[2])
    if include is None:
        ifields = [f for f in form]
    else:
        include = [f.strip() for f in include.split(',')]
        ifields = []
        for ifield in include:
            for field in form:
                if field.name == ifield:
                    ifields.append(field)
    try:
        bootstrap_float = str(params[1]).lower() == 'float'
    except IndexError:
        bootstrap_float = False
    ifields = grouper(columns, ifields)
    colspan = int(12/columns)
    context['form'] = form
    context['ifields'] = ifields
    context['colspan'] = colspan
    context['layout'] = layout
    context['float'] = bootstrap_float
    return get_template('bootstrap_toolkit/form.html').render(context)
