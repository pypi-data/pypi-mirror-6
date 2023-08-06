========================
django-url-breadcrumbs
========================

.. image:: https://drone.io/bitbucket.org/slafs/django-url-breadcrumbs/status.png
       :target: https://drone.io/bitbucket.org/slafs/django-url-breadcrumbs/latest


An app for generic breadcrumbs in Django (>= 1.4).

The idea is to make breadcrumbs out of parts of an url path. This application assumes that your url patterns are well structured. For example like this::

    /                                               # root path
    /application/                                   # root of an app/module
    /application/object_type/                       # list of specific objects
    /application/object_type/some_object/           # details of specific object
    /application/object_type/some_object/edit/      # edit (or any other operations) of a specific object


Installation
===============

1. Install the package from PyPi. For example via pip::

    pip install django-url-breadcrumbs

2. Add ``urlbreadcrumbs`` to INSTALLED_APPS::

    INSTALLED_APPS = ( 
        ...
        'urlbreadcrumbs',
        ...
    )

3. Make sure you have a request context processor ``django.core.context_processors.request`` in your ``TEMPLATE_CONTEXT_PROCESSORS``.


Usage
==========

Let's assume you have your urls in a form:

in ``ROOT_URLCONF``::

    from django.conf.urls import patterns, include, url
    from myproject.views import some_view

    urlpatterns = patterns('',
        url(r'^$', some_view, {'template' : 'index.html'}, name='index'),
        url(r'^test1/', include('test1.urls')),
    )


``urls.py`` in application called ``test1``::

    from django.conf.urls import patterns, include, url
    from test1.views import some_view

    urlpatterns = patterns('',
        url(r'^example/$', some_view, {'template' : 't1.html'}, name='t1home'),
    )


In order to define your breadcrumbs you can make a mapping in ``settings.py`` like this::

    URLBREADCRUMBS_NAME_MAPPING = {
        'index'  : 'Home page',
        't1home' : 'Index page of Test1',
    }


Then somwhere in your base template (lets call it ``base.html``) you can write this::

    {% load urlbreadcrumbs_tags %}
    {% render_breadcrumbs %}

or you can specify your own template::

    {% render_breadcrumbs "test1/mybreadcrumbs_template.html" %}

Also you can just include your breadcrumbs template::

    {% include "test1/mybreadcrumbs_template.html" %}

But to use it like this make sure you've added a context procesor ``urlbreadcrumbs.context_processors.build_breadcrumbs``
in your ``TEMPLATE_CONTEXT_PROCESSORS`` setting.

In your template you have one additional context variable called ``breadcrumbs`` 
which is a list of two-tuples containing name and url of a breadcrumb.
The default template used by ``django-url-breadcrumbs`` (``urlbreadcrumbs/default.html``) looks like this::

    {% for n,u in breadcrumbs %}
        {% if not forloop.last %}
            <a href="{{ u }}">{{ n }}</a> &raquo;
        {% else %}
            {{ n }}
        {% endif %}
    {% endfor %}

So now, assuming template ``t1.html`` is extending ``base.html``, when viewing ``/test1/example/``
you should see something like this ``Home page » Index page of Test1``.

Another way of specyfing a name for a breadcrumb is to use a custom ``url`` function in your ``urls.py``.
Instead of defining a mapping in ``URLBREADCRUMBS_NAME_MAPPING`` setting you can do this in ``urls.py`` of your ``ROOT_URLCONF`` and ``test1`` application::

    from django.conf.urls import patterns, include, url
    from urlbreadcrumbs import url as burl

    urlpatterns = patterns('',
        ...
        burl(r'^test1/', include(test1_urls)),
        ...
    )

and ::

    from django.conf.urls import patterns, include, url
    from test1.views import some_view
    from urlbreadcrumbs import url as burl

    urlpatterns = patterns('',
        burl(r'^example/$', some_view, {'template' : 't1.html'}, name='t1home', verbose_name='Index page of Test1'),
    )

This should work as in previous example.

Development
===============

Ideas and/or bug reports are welcome. Consider reporting an issue on https://bitbucket.org/slafs/django-url-breadcrumbs/issues?status=new&status=open

Pull requests are also welcome ;).

To start working on this app get the source from Bitbucket::

    hg clone https://bitbucket.org/slafs/django-url-breadcrumbs

and in a newly created virtualenv do this::

    pip install -r dev_requirements.txt
    python setup.py test

Testing
-----------

django-url-breadcrumbs uses `pytest`_ for running it's test suite and `tox`_ for checking it's compatibilty
with different Python and Django versions.

In order to perform tests with your current python and django installation do this::

    python setup.py test

To test it with different python and django versions run this::

    tox

.. _tox: http://tox.readthedocs.org
.. _pytest: http://pytest.org

