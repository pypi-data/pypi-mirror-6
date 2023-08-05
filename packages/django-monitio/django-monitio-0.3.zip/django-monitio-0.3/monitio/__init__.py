# This must be imported first - the DEFAULT_TAGS must be updated
# before import of monitio.api
from monitio.constants import *
from django.contrib import messages

messages.DEFAULT_TAGS.update(DEFAULT_TAGS)

from monitio.api import *

