from django import template
from django.core.exceptions import ImproperlyConfigured
from urlbreadcrumbs.context_processors import build_breadcrumbs

register = template.Library()


@register.simple_tag(name="render_breadcrumbs", takes_context=True)
def render_breadcrumbs(context, template_name = "urlbreadcrumbs/default.html"):
    request = context.get('request', None)
    if request is None:
        raise ImproperlyConfigured("You have to provide a request object in context")

    c_vars = build_breadcrumbs(request)
    t = template.loader.get_template(template_name)
    context.update(c_vars)
    return t.render(context)
