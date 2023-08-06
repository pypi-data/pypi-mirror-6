==========================
Zinnia-spam-checker-mollom
==========================

Zinnia-spam-checker-mollom is a package providing spam protection on
comments for `django-blog-zinnia`_ via `Mollom`_.

Installation
============

* Install the package on your system: ::

  $ pip install zinnia-spam-checker-mollom

  `PyMollom`_ will also be installed as a dependency.

* Put this setting to enable the spam checker backend:

  ``ZINNIA_SPAM_CHECKER_BACKENDS = ('zinnia_mollom',)``

* Define these following settings with your credentials:

  ``MOLLOM_PUBLIC_KEY`` Your Mollom public key

  ``MOLLOM_PRIVATE_KEY`` Your Mollom private key

Get a free account at http://mollom.com/pricing if you don't already have one.

.. _django-blog-zinnia: http://django-blog-zinnia.com
.. _Mollom: http://mollom.com/
.. _PyMollom: https://github.com/itkovian/PyMollom
