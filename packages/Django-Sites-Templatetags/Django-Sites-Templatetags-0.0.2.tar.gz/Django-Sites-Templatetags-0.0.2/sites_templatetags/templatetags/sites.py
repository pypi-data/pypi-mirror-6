from django import template
from django.contrib.sites.models import get_current_site

register = template.Library()


@register.assignment_tag(takes_context=True)
def current_site(context):
    request = context['request']
    return get_current_site(request)
