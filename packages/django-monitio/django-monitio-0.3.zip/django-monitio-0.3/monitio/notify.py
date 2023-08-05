import json
import warnings

from django.core.mail import send_mail
from django_sse.redisqueue import send_event

from monitio.conf import settings
from monitio import testutil
from monitio import constants
from monitio.models import Monit


def email(level, message, extra_tags, subject, user, from_user):
    if not user or not user.email:
        raise Exception(
            'Function needs to be passed a `User` object with valid email address.')
    send_mail(subject, message, from_user.email if from_user else None,
              [user.email], fail_silently=False)


def via_email(message_pk):
    try:
        message = Monit.objects.get(pk=message_pk)
    except Monit.DoesNotExist:
        return

    return email(
        message.level, message.message, message.extra_tags,
        message.subject, message.user, message.from_user)


def sse(level, pk, message, extra_tags, subject, user, from_user):
    """
    :type user: basestring
    :type from_user: basestring
    """

    msg = json.dumps(dict(
        level=level,
        pk=pk,
        message=message,
        extra_tags=extra_tags,
        subject=subject,
        from_user=from_user))

    if settings.TESTING:
        #
        # Please see notes in monitio.conf.settings and monitio.notify.sse
        #
        warnings.warn(
            "Testing mode - I will fake sending SSE messages and bypass Redis")
        testutil.MESSAGES.append(msg)
        return

    send_event("message", msg, channel=user)


def via_sse(message_pk):
    try:
        message = Monit.objects.get(pk=message_pk)
    except Monit.DoesNotExist:
        return

    _to = None
    if message.user:
        _to = message.user.username

    _from = None
    if message.from_user:
        _from = message.user.username

    return sse(
        message.level, message.pk, message.message, message.extra_tags,
        message.subject, _to, _from)
