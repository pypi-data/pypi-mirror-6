from django.core.urlresolvers import get_resolver, Resolver404
from django.conf import settings
from urlbreadcrumbs.conf import NAME_MAPPING, PATH_SPLIT_CHAR, RESOLVER
from django.utils.importlib import import_module


if RESOLVER is not None:
    resolver_package, resolver_class_name = RESOLVER.rsplit(".", 1)
    resolver_class = getattr(import_module(resolver_package), resolver_class_name)
    resolver = resolver_class(r'^' + PATH_SPLIT_CHAR, settings.ROOT_URLCONF)
else:
    resolver = None

RESOLVER_INSTANCE = resolver


def build_breadcrumbs(request):
    if RESOLVER_INSTANCE is None:
        import warnings
        warnings.warn("You should provide a URLBREADCRUMBS_RESOLVER in your settings "
                      "(eg. 'urlbreadcrumbs.BreadRegexURLResolver') "
                      "in order to correctly use the url function provided by django-url-breadcrumbs")

    if RESOLVER_INSTANCE is not None:
        resolver = RESOLVER_INSTANCE
    else:
        resolver = get_resolver(settings.ROOT_URLCONF)

    ret_list = []  # list of pairs (name, path)

    path = request.path_info
    parts = path.split(PATH_SPLIT_CHAR)
    if not parts[-1]:
        parts = parts[:-1]  # loose last empty element
    try_path = ""
    for part in parts:
        try_path = try_path + part + PATH_SPLIT_CHAR

        try:

            resolver_match = resolver.resolve(try_path)
            if resolver_match is not None:

                nspace, url_name = resolver_match.namespace, resolver_match.url_name
                lookup = url_name
                if nspace:
                    lookup = nspace + ":" + url_name

                from_mapping = NAME_MAPPING.get(lookup, False)
                if from_mapping:
                    name = from_mapping
                elif hasattr(resolver_match, 'breadcrumb_verbose_name') and \
                        resolver_match.breadcrumb_verbose_name is not None:
                    name = resolver_match.breadcrumb_verbose_name
                else:
                    name = resolver_match.url_name

                ret_list.append((name, try_path))

        except Resolver404:
            pass

    return {'breadcrumbs': ret_list}
