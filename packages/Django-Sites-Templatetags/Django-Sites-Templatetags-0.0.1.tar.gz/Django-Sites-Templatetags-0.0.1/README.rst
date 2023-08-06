=========================
Django-Sites-Templatetags
=========================

The missing templatetags to get the current site from ``django.contrib.sites``.

Installation
============

Use your favorite method to get it from pypi, for example:

::

    pip install django-sites-templatetags

Then add ``sites_templatetags`` to your ``INSTALLED_APPS``.


Usage
=====

In a template:

::

    {% load sites %}
    {% current_site as site %}
    You are viewing {{ site.domain }}.
