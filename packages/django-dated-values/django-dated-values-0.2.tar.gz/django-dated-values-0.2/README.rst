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

The usage is fairly straight forward. You need to add ``DatedValueType``
instances for every content type, that you want values to be added to.

The ``decimal_places`` field allows you to lower the amount of decimal places
for form validation. It defaults to 2 and its max is 8.

.. note:: Using postgres, it stores the full range of decimal places, no matter
    if you input less.

If you set ``hidden`` to ``True`` using the default template automatically
hides the values in the form. You can e.g. use it to log values in the
background without them being visible for users.

If you just set ``editable`` to ``True`` using the default template will
render only the values and no input fields.

Once you've set that up and visit the management view, you will see a form
table which holds all the values from all defined types for that item.
The url kwargs require ``ctype_id`` and ``object_id``. An example
implementation might be:

.. code-block:: python

    class MyModel(models.Model):

    ...  # my fields and other things go here

    def get_management_url(self):
        """Returns the management url from django-dated-values."""
        ctype = ContentType.objects.get_for_model(self.__class__)
        return reverse('dated_values_management_view', kwargs={
            'ctype_id': ctype.id, 'object_id': self.id})


Settings
--------

The ``DATED_VALUES_ACCESS_ALLOWED`` setting expects a function, that takes the
user and the content object as arguments. It is required to define the access
permission for the values management view. Default is as follows:

.. code-block:: python

    DATED_VALUES_ACCESS_ALLOWED = lambda user, obj=None: user.is_staff

.. note:: superusers will always be able to open the view, regardless of what
    is set here.

You can change the lenght of displayed items, defaulting to 14 (2 weeks) by
setting ``DATED_VALUES_DISPLAYED_ITEMS``:

.. code-block:: python

    # this will only show 1 week
    DATED_VALUES_DISPLAYED_ITEMS = 7


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
