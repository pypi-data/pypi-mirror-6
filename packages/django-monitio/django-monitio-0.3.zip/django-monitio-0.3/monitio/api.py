from monitio import notify
from monitio import constants

def add_message(request, level, message, extra_tags='', fail_silently=False,
                subject='', user=None, email=False, sse=False, from_user=None,
                expires=None, close_timeout=None, url=None):
    return request._messages.add(level, message, extra_tags, subject, user,
                                 from_user, expires, close_timeout,
                                 sse, email, url)


def info(request, message, extra_tags='', fail_silently=False, subject='',
         user=None, email=False, sse=False, from_user=None, expires=None,
         close_timeout=None, url=None):
    """
    """
    level = constants.INFO
    return add_message(request, level, message, extra_tags, fail_silently,
                       subject, user, email, sse, from_user, expires,
                       close_timeout, url)


def warning(request, message, extra_tags='', fail_silently=False, subject='',
            user=None, email=False, sse=False, from_user=None, expires=None,
            close_timeout=None, url=None):
    """
    """
    level = constants.WARNING
    return add_message(request, level, message, extra_tags, fail_silently,
                       subject, user, email, sse, from_user, expires,
                       close_timeout, url)


def debug(request, message, extra_tags='', fail_silently=False, subject='',
          user=None, email=False, sse=False, from_user=None, expires=None,
          close_timeout=None, url=None):
    """
    """
    level = constants.DEBUG
    return add_message(request, level, message, extra_tags, fail_silently,
                       subject, user, email, sse, from_user, expires,
                       close_timeout, url)


def create_message(to_user, level, message, from_user=None, extra_tags='',
                   subject='', expires=None, close_timeout=None, sse=False,
                   email=False, url=None):
    """
    Use this method to create message without a request object - this can
    be used in command-line utilities, celery backend or for testing.
    """

    from monitio.storage import PersistentMessageStorage
    class request:
        user = to_user
        session = {}

    request.messages = PersistentMessageStorage(request)

    request.messages.add(level=level, message=message, extra_tags=extra_tags,
                         subject=subject, from_user=from_user, expires=expires,
                         close_timeout=close_timeout, sse=sse, email=email,
                         url=url)
