=====================
Django-Sites-Lockdown
=====================

Sometimes with Django you need to include the sites framework because an app
requires it, but you don't really want or need staff to be able to add or
delete sites in the admin panel. This app removes the capability to add or
remove sites.

This is a very simple bit of functionality but it it useful enough to have an
app so as not to have to repeat the process for every new django site.

Installation
============

Use your favorite method to get it from pypi, for example:

::

    pip install django-sites-lockdown

Then add ``sites_lockdown`` to your ``INSTALLED_APPS``.
