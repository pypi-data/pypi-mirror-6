=============================
django_reform
=============================

.. image:: https://badge.fury.io/py/django_reform.png
    :target: http://badge.fury.io/py/django_reform
    
.. image:: https://travis-ci.org/alixedi/django_reform.png?branch=master
        :target: https://travis-ci.org/alixedi/django_reform

.. image:: https://pypip.in/d/django_reform/badge.png
        :target: https://crate.io/packages/django_reform?version=latest


Control of widgets in templates sans BS.

Installation
------------

We are at the cheeseshop: ::

	pip install django_reform

Usage
-----

To use django_reform in a project:

1. Include it in INSTALLED_APPS in your settings file.

2. Render your forms like so: ::
	
	{% load reform %}
	{{ reform form }}

3. Open reform/templates/reform/field.html - by default rendering HTML5 input types. Go ahead and tweak: ::

	{% load widget_tweaks reform %}
	{% with field_type=field|get_form_field_type %}
	    {% if field_type == 'DateField' %}
	        {% render_field field type="date" %}
	    {% elif field_type == 'EmailField' %}
	        {% render_field field type="email" %}
	    {% elif field_type == 'URLField' %}
	        {% render_field field type="url" %}
	    {% else %}
	        {{ field }}
	    {% endif %}
	{% endwith %}

4. Advanced usage - controlling which fields to include, order of the fields as well as number of columns in which the form is rendered. The code below will render a form with the given fields, bootstrap vertical layout, no float and using 3-columns: ::

	{% reform form 'email, number, url, time' 'vertical,false,3' %}

Sans BS as promised :)
