|wq.db|

`wq.db <http://wq.io/wq.db>`__ is a collection of Python modules for
building robust, flexible schemas and REST APIs for use in creating
field data collection apps and (more generally) mobile-first websites
with progressive enhancement. wq.db is the backend component of
`wq <http://wq.io>`__ and is geared primarily for use with
`wq.app <http://wq.io/wq.app>`__, though it can be used separately.
wq.db is built on the `Django <https://www.djangoproject.com/>`__
platform.

|Build Status|

Getting Started
---------------

.. code:: bash

    pip install wq.db
    # Or, if using together with wq.app and/or wq.io
    pip install wq

See `the documentation <http://wq.io/docs/>`__ for more information.

Features
--------

wq.db has two primary components: a REST API generator
(`wq.db.rest <http://wq.io/docs/about-rest>`__) and a collection of
schema design patterns
(`wq.db.patterns <http://wq.io/docs/about-patterns>`__) that facilitate
flexible database layouts.

`wq.db.rest <http://wq.io/docs/about-rest>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extends the excellent `Django REST
Framework <http://django-rest-framework.org>`__ with a collection of
views, serializers, and context processors useful for creating a
progresively enhanced website that serves as its own mobile app and `its
own REST API <http://wq.io/docs/website-rest-api>`__. The core of the
library (`app.py <http://wq.io/docs/app.py>`__) includes an admin-style
Router that connects REST urls to registered models, and provides a
descriptive `configuration object <http://wq.io/docs/config>`__ for
consumption by `wq.app's client-side
router <http://wq.io/docs/app-js>`__. wq.db.rest also includes a
CRS-aware GeoJSON serializer/renderer.

`wq.db.patterns <http://wq.io/docs/about-patterns>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A collection of recommended design patterns
(`annotate <http://wq.io/docs/annotate>`__,
`identify <http://wq.io/docs/identify>`__,
`locate <http://wq.io/docs/locate>`__, and
`relate <http://wq.io/docs/relate>`__) that provide long-term
flexibility and sustainability for user-maintained data collection
applications. These patterns are implemented as installable Django apps.

Batteries Included
~~~~~~~~~~~~~~~~~~

Like Django itself, wq.db includes a
`contrib <http://wq.io/docs/?section=contrib>`__ module that provides
additional functionality not considered to be part of the "core"
library.

`chart <http://wq.io/docs/chart>`__
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Generates time series and box plot data for rendering by
`wq/chart.js <http://wq.io/docs/chart-js>`__. Powered by `Django REST
Pandas <https://github.com/wq/django-rest-pandas>`__ and
`vera <http://wq.io/vera>`__.

`dbio <http://wq.io/docs/dbio>`__
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Load data from external files into the database. Powered by
`wq.io <http://wq.io/wq.io>`__, `files <http://wq.io/docs/files>`__, and
`vera <http://wq.io/vera>`__.

`files <http://wq.io/docs/files>`__
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Generic file manager. Supports using the same ``FileField`` for both
images and files. Also includes a URL-driven thumbnail generator.

`search <http://wq.io/docs/search>`__
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Views for searching and disambiguating models using the
`identify <http://wq.io/docs/identify>`__ and
`annotate <http://wq.io/docs/annotate>`__ patterns.

`vera <http://wq.io/vera>`__
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Reference implementation of the `ERAV <http://wq.io/docs/erav>`__ model,
an extension to EAV with support for maintaining multiple versions of an
entity.

.. |wq.db| image:: https://raw.github.com/wq/wq/master/images/256/wq.db.png
   :target: http://wq.io/wq.db
.. |Build Status| image:: https://travis-ci.org/wq/wq.db.png?branch=master
   :target: https://travis-ci.org/wq/wq.db
