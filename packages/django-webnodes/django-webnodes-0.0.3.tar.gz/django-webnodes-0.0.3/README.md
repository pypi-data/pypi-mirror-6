django-webnodes
===============

The goal of `django-webnodes` is to create a new way of writing django templates which is fully compatible with the current django templating infrastructure. 

It's born to make it easy to support standard, reusable `bussiness components` across your application.

`django-webnodes` are like special functional calls to render components of your page.

## Usage:

This use as django templatetags

	{% webnode node_name [value1 value2 ... key1=value1 key2=value2 ...] %}

- ``value1``: position value passed as ``value1`` in ``get_context()`` and ``render()`` methods
- ``key1=value1``: dictionary key-value pairs passed as ``key1`` in ``get_context()`` and ``render()`` methods

## Demo

For example, if you are implementing a app statistics website, and you want to have app ratings appear on both list page and detail page, you can make an `RatingsNode` to render them on both pages.

First, create a Python module for your webnodes, e.g., webnodes.py(place it in ``yourapp`` module)

    from webnodes import WebNode


    class RatingsNode(WebNode):

    	template = 'webnodes/ratings.html'

        def get_context(self, app_id):
        	...
	        ratings = ...
    	    return {'ratings': ratings}

Calling from template:

    {% load webnode %}

    <p>{% webnode RatingsNode app.id %}</p>

## Extension

If you want see this webnode independently, you can add this in your urls' urlpatterns

	url(r'^webnodes/', include('webnodes.ext.urls'))

Then open `http://127.0.0.1:8000/webnodes/RatingsNode?app_id=414603431` in your browser, you will see it.

## Why use this?

1. Decoupling the logic of front-end and back-end separately;
2. Make each component as a webnode will improve cohesion(because each component's template and data(include the logic of fetch data) are always strongly correlated);
3. We can test each component independently;
4. easy to realize partial renewal.

## Todos

support css and javascript

# Refs

Inspired by [tornado UI Module](https://github.com/facebook/tornado/blob/master/tornado/web.py), [django custom templatetags](https://docs.djangoproject.com/en/dev/howto/custom-template-tags/).

Based on [django-widgets(1)](https://code.google.com/p/django-widgets) and [django-widgets(2)](https://github.com/marcinn/django-widgets)
