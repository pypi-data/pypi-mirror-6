#!/usr/bin/env python
from django.conf import global_settings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
INSTALLED_APPS = (
    'urlbreadcrumbs',
    'urlbreadcrumbs.tests',
)
SITE_ID = 1
SECRET_KEY = 'super-secret'
ROOT_URLCONF = 'urlbreadcrumbs.tests.urls'
TEMPLATE_CONTEXT_PROCESSORS = \
    global_settings.TEMPLATE_CONTEXT_PROCESSORS + \
    ('django.core.context_processors.request',  # for ``render_breadcrumbs`` templatetag
     'urlbreadcrumbs.context_processors.build_breadcrumbs',)
URLBREADCRUMBS_NAME_MAPPING = {
    'index'  : 'A title for a home page',
    't1home' : 'Index page of Test1',
}
