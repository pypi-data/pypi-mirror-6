Django APSara Purchasing Module
===============================

.. image:: https://travis-ci.org/bitmazk/django-aps-purchasing.png?branch=master   
   :target: https://travis-ci.org/bitmazk/django-aps-purchasing

The purchasing module for django-apsara.

Prerequisites
-------------

This module needs `django-aps-bom <https://github.com/bitmazk/django-aps-bom>`_.
It will be automatically installed via this modules' `setup.py`.


Installation
------------

To get the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/bitmazk/django-aps-purchasing.git#egg=aps_purchasing

Add ``aps_purchasing`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'aps_purchasing',
    )

Add the ``aps_purchasing`` URLs to your ``urls.py``

.. code-block:: python

    urlpatterns = patterns('',
        ...
        url(r'^aps-purchasing/', include('aps_purchasing.urls')),
    )

Don't forget to migrate your database

.. code-block:: bash

    ./manage.py migrate aps_purchasing


Usage
-----

TODO: Describe usage or point to docs. Also describe available settings and
templatetags.


Contribute
----------

If you want to contribute to this project, please perform the following steps

.. code-block:: bash

    # Fork this repository
    # Clone your fork
    mkvirtualenv -p python2.7 django-aps-purchasing
    make develop

    git co -b feature_branch master
    # Implement your feature and tests
    fab test  # Run the tests and check coverage
    git add . && git commit
    git push -u origin feature_branch
    # Send us a pull request for your feature branch
