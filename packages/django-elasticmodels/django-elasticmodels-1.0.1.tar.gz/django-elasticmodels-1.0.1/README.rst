========
 README
========

django-elasticmodels is a convenient tool to map your Django models to
ElasticSearch mappings.

Project details
===============

:Code:           https://bitbucket.org/jvennik/django-elasticmodels
:Documentation:  #
:Issue tracker:  https://bitbucket.org/jvennik/django-elasticmodels/issues
:License:        BSD 3-clause; see LICENSE file


Quick install
=============

Latest released version::

    $ pip install django-elasticmodels

Usage
=============

To use django-elasticmodels in your Django project:

    1. Add ``'elasticmodels'`` to your ``INSTALLED APPS`` setting.
    2. Add ``'ELASTICSEARCH_HOST'`` (string)
    3. Add ``'ELASTICSEARCH_MODELS'`` (list) >> ``'["yourapp.yourmodel",]'`` to your settings file
    4. [Optional] Add ``'ELASTICSEARCH_CUSTOM_TYPES'`` (dict) to your settings file if you want to specify a specific field type yourself >> Example: ``'"geo_location": {"type": "geo_point"}'``
    5. [Optional] Add ``'ELASTICSEARCH_NON_MODEL_FIELDS'`` (list). Here you can add fields that are not present on your model >> Example: ``'{"snippet": {"type": "string"}}'``
    6. Run ./manage.py create_indexes

Examples will be added at a later date.
