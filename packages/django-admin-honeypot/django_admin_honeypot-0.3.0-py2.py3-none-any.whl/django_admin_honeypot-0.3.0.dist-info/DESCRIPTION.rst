django-admin-honeypot
=====================

A fake Django admin login screen to notify admins of attempted unauthorized
access. This app was inspired by discussion in and around Paul McMillan's
security talk at DjangoCon 2011.

|travis-ci|_ |coverage-io|_ |downloads|_

.. |travis-ci| image:: https://secure.travis-ci.org/dmpayton/django-admin-honeypot.png
.. _travis-ci: https://travis-ci.org/dmpayton/django-admin-honeypot

.. |coverage-io| image:: https://coveralls.io/repos/dmpayton/django-admin-honeypot/badge.png
.. _coverage-io: https://coveralls.io/r/dmpayton/django-admin-honeypot

.. |downloads| image:: https://pypip.in/d/django-admin-honeypot/badge.png
.. _downloads: https://pypi.python.org/pypi/django-admin-honeypot


Basic Usage:

* Add ``admin_honeypot`` to ``settings.INSTALLED_APPS``
* Update urls.py::

    urlpatterns = patterns(''
        ...
        url(r'^admin/', include('admin_honeypot.urls')),
        url(r'^secret/', include(admin.site.urls)),
    )


