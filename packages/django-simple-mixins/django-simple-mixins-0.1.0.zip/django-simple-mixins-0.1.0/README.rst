==========================
django-simple-mixins
==========================

What is it?
===========

django-simple-mixins is a simple Django App that contains some Mixins to use for Django's Class Based Views.

Installation
============

You can do any of the following to install ``django-simple-mixins``

- Run ``pip install django-simple-mixins``.
- Run ``easy_install django-simple-mixins``.
- Download or "git clone" the package and run ``setup.py``.
- Download or "git clone" the package and add ``simplemixins`` to your PYTHONPATH.

Usage
=====

For example if you'd like to use the ``CacheMixin``::

    from django.views.generic import ListView
    
    from simplemixins.mixins import CacheMixin

    class ArticleListView(CacheMixin, ListView):
        cache_timeout = 60 * 15     # 900 – that is, 15 minutes multiplied by 60 seconds per minute.
        model = Article

Requirements
============

`Django>=1.5
<https://github.com/django/django/>`_
