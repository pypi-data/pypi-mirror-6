# -*- encoding: utf-8 -*-

#
# This package, django-monitio, needs to know, if we are runing the tests
# or not.
#
# This is pretty important, as by the time of this writing, LiveServerTestCase
# will block when testing monitio-enabled web pages, because sse view
# will block the server thread. So, let's set this value and give
# sse views a hint to behave differently.
#
# This is a new issue, I suppose, as there are no googleable rants about
# this limitation of LiveServerTestCase at this moment. Perhaps "one thread
# should be enough for everybody", just like 640k :-)
#

import sys

from django.conf import settings

TESTING = getattr(settings, 'TESTING', 'test' in sys.argv[:2])

if TESTING:
    # This seems to be another problem. We should attach to this list
    # every possible port of testserver.
    settings.CORS_ORIGIN_WHITELIST = (
        'localhost:8081'
    )
