django-urlconverter: Django automatic view parameters conversion
================================================================

The ``django-urlconverter`` package provides an easy way to convert view arguments
from simple types to complex ones, like models, or just do some processing using robust syntax.
Most interesting application of the package is to convert view arguments which are object ids (from database via ORM)
to the instances of those objects (Models).


.. image:: https://api.travis-ci.org/paylogic/django-urlconverter.png
   :target: https://travis-ci.org/paylogic/django-urlconverter
.. image:: https://pypip.in/v/django-urlconverter/badge.png
   :target: https://crate.io/packages/django-urlconverter/
.. image:: https://coveralls.io/repos/paylogic/django-urlconverter/badge.png?branch=master
   :target: https://coveralls.io/r/paylogic/django-urlconverter


Installation
------------

.. sourcecode::

    pip install django-urlconverter


Usage
-----

models.py:

.. code-block:: python

    from django.db import models


    class FooBar(models.Model):
        """Foo Bar model."""
        title = models.CharField(max_length=100)

converters.py:

.. code-block:: python

    from .models import FooBar


    class Foo(object):
        """Foo converter. Convert an object id to FooBar instance."""
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def __call__(self, value, request, *args, **kwargs):
            return FooBar.objects.get(pk=value)

settings.py:

.. code-block:: python

    URL_CONVERTERS = {
        'Foo': 'converters.Foo',  # Converts to 'FooBar instance'
    }

urls.py:

.. code-block:: python

    from django.conf.urls.defaults import patterns
    from django_urlconverter import converted_arguments_url

    urlpatterns = patterns('views',
        converted_arguments_url(r'^foos/<Foo:foo2>/', 'bar'),
    )

views.py:

.. code-block:: python

    def bar(request, foo2):
        """View function which gets a converted foo2.
        the foo2 will be a converted parameter, which is the result of Foo converter
        """
        return foo2.title


Contact
-------

If you have questions, bug reports, suggestions, etc. please create an issue on
the `GitHub project page <http://github.com/paylogic/django-urlconverter>`_.


License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_

See `<LICENSE.txt>`_


© 2013 Paylogic International.
