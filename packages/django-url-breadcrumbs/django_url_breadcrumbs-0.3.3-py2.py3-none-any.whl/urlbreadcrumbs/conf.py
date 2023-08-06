# TODO: make this compatible with django-appconf

from django.conf import settings

NAME_MAPPING = getattr(settings, 'URLBREADCRUMBS_NAME_MAPPING', {})
PATH_SPLIT_CHAR = getattr(settings, 'URLBREADCRUMBS_PATH_SPLIT_CHAR', r'/')

# set this to 'urlbreadcrumbs.BreadRegexURLResolver'
# if you want to use custom url function (provided by urlbreadcrumbs) within your urlpatterns
RESOLVER = getattr(settings, 'URLBREADCRUMBS_RESOLVER', 'urlbreadcrumbs.BreadRegexURLResolver')
