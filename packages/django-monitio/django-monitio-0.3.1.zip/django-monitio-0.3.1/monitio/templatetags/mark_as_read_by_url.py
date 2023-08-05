# -*- encoding: utf-8 -*-

from django import template
from django.utils.functional import SimpleLazyObject
from monitio.models import Monit


register = template.Library()


@register.simple_tag(takes_context=True)
def mark_as_read_by_url(context):
    request = context['request']

    # request.user may be a SimpleLazyObject instance
    try:
        user_id = request.user.pk
    except AttributeError:
        return ''

    if user_id is None:
        return ''

    url = request.get_full_path()
    Monit.objects.filter(user_id=user_id, read=False, url=url).update(read=True)
    return ''