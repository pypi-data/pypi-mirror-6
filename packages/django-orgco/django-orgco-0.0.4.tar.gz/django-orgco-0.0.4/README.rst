django-orgco
============

Copyright (c) 2013, Friedrich Paetzke (f.paetzke@gmail.com)
All rights reserved.

django-orgco implements a template tag to use orgco easily in django templates.

How to use
----------

Install the package via ``pip``

.. code:: bash

    $ pip install django-orgco

Add the package to your installed apps in settings.py.

.. code:: python

    INSTALLED_APPS = (
        ...
        'django_orgco',
        ...
    )

Then use it. Here is an example:

my_template.html:

.. code:: html

    {% load orgdoc %}
    
    {% orgdoc %}
    * header is here
    
    - short1 :: long1
    - short2 :: long2
    - short3 :: long3
    
    | th1 | th2 |
    |-----+-----|
    | td1 | td2 |
    {% endorgdoc %}

To enable code highlighting add *highlight* to *orgdoc*:

.. code:: html

    {% orgdoc highlight %}
    is_ok = True
    {% endorgdoc %}
