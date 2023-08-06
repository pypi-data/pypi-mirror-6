================
djangocms-blogit
================

**Project is a development stage (pre-alpha)**

A simple blog plugin for django-cms.

Dependencies
------------

* `django-cms`_ == 2.4.3
* `django-filer`_ == 0.9.5
* `django-hvad`_ == 0.3
* `django-taggit`_ == 0.10

Installation
------------

To install ``djangocms-blogit`` with ``pip`` run::

    $ pip install djangocms-blogit


Setup
-------------

Setup `django-cms`_ and `django-filer`_ than add to ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...
        'hvad',
        'taggit',
        'blogit',
        ...
    )


Settings
-------------

BLOGIT_POSTS_PER_PAGE
    Number of posts displayed per page.
    Defaults to 5.

BLOGIT_LIST_TEMPLATE
    Path to list template. Defaults to ``blogit/list.html``

BLOGIT_DETAIL_TEMPLATE
    Path to detail template. Defaults to ``blogit/detail.html``

BLOGIT_AUTHOR_LINK_TYPE_CHOICES
    Link type choices for authors. List of tuples.

BLOGIT_CATEGORY_URL, BLOGIT_AUTHOR_URL
    Default url names.

BLOGIT_CATEGORY_URL_TRANSLATION, BLOGIT_AUTHOR_URL_TRANSLATION
    Url translation.
    ::
        BLOGIT_CATEGORY_URL_TRANSLATION = (
            ('en', 'category'),
            ('hr', 'kategorija'),
            ...
        )


.. _django-cms: https://github.com/divio/django-cms
.. _django-filer: https://github.com/stefanfoulis/django-filer
.. _django-hvad: https://github.com/kristianoellegaard/django-hvad
.. _django-taggit: https://github.com/alex/django-taggit
