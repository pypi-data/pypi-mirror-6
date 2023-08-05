Django Dated Values
===================

A reusable Django app that allows adding dated decimal values to any Django model.

Installation
------------

To get the latest stable release from PyPi

.. code-block:: bash

    pip install django-dated-values

To get the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/bitmazk/django-dated-values.git#egg=dated_values

TODO: Describe further installation steps (edit / remove the examples below):

Add ``dated_values`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'dated_values',
    )

Add the ``dated_values`` URLs to your ``urls.py``

.. code-block:: python

    urlpatterns = patterns('',
        ...
        url(r'^dated-values/', include('dated_values.urls')),
    )

Don't forget to migrate your database

.. code-block:: bash

    ./manage.py migrate dated_values


Add css or write your own custom styles.

.. code-block:: html

    {% load static %}
    <link href="{% static "dated_values/css/dated_values.css" %}" rel="stylesheet">

Usage
-----

TODO: Describe usage or point to docs. Also describe available settings and
templatetags.


Settings
--------
DATED_VALUES_ACCESS_ALLOWED = lambda user: user.is_staff
DATE_FORMAT = getattr(settings, 'DATED_VAUES_DATE_FORMAT', '%d-%m-%Y')


Contribute
----------

If you want to contribute to this project, please perform the following steps

.. code-block:: bash

    # Fork this repository
    # Clone your fork
    mkvirtualenv -p python2.7 django-dated-values
    make develop

    git co -b feature_branch master
    # Implement your feature and tests
    git add . && git commit
    git push -u origin feature_branch
    # Send us a pull request for your feature branch
