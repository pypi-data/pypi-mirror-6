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
	
	{% load bootstrap_toolkit %}
	{{ form|as_bootstrap }}

3. Open reform/field.html ::

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

Sans BS as promised :)
