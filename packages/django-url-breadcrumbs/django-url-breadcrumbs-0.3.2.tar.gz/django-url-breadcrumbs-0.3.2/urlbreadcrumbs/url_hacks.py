from django.conf.urls import url as djurl
from django.core.urlresolvers import RegexURLPattern, RegexURLResolver, ResolverMatch, Resolver404
from django.utils.encoding import smart_str


class BreadRegexURLPattern(RegexURLPattern):

    verbose_name = None

    def resolve(self, *args, **kwargs):
        rm = super(BreadRegexURLPattern, self).resolve(*args, **kwargs)
        if rm:
            rm.breadcrumb_verbose_name = self.verbose_name
        return rm


class BreadRegexURLResolver(RegexURLResolver):

    def resolve(self, path):
        '''
        this is rewritten from django.core.urlresolvers
        because playing with URL patterns and resolvers in Django<=1.4 is weird.
        Probably because of the recursion.
        Really! Try it yourself.
        FIXME: As of Django 1.4 this shouldn't be necessary!
        '''
        tried = []
        match = self.regex.search(path)
        if match:
            new_path = path[match.end():]
            for pattern in self.url_patterns:
                try:
                    sub_match = pattern.resolve(new_path)
                except Resolver404 as e:
                    sub_tried = e.args[0].get('tried')
                    if sub_tried is not None:
                        tried.extend([[pattern] + t for t in sub_tried])
                    else:
                        tried.append([pattern])
                else:
                    if sub_match:
                        sub_match_dict = dict([(smart_str(k), v) for k, v in match.groupdict().items()])
                        sub_match_dict.update(self.default_kwargs)
                        for k, v in sub_match.kwargs.items():
                            sub_match_dict[smart_str(k)] = v
                        res_match = ResolverMatch(sub_match.func, sub_match.args, sub_match_dict,
                                                  sub_match.url_name,
                                                  self.app_name or sub_match.app_name,
                                                  [self.namespace] + sub_match.namespaces)
                        res_match.breadcrumb_verbose_name = getattr(sub_match,
                                                                    'breadcrumb_verbose_name', None)

                        return res_match
                    tried.append([pattern])
            raise Resolver404({'tried': tried, 'path': new_path})
        raise Resolver404({'path' : path})


def url(*args, **kwargs):

    vn = kwargs.pop("verbose_name", None)
    reg = djurl(*args, **kwargs)

    if isinstance(reg, RegexURLPattern):
        reg.__class__ = BreadRegexURLPattern
        reg.verbose_name = vn
    elif isinstance(reg, RegexURLResolver):
        reg.__class__ = BreadRegexURLResolver

    return reg
