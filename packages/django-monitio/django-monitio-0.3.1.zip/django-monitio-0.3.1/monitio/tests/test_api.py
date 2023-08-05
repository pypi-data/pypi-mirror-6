# -*- encoding: utf-8 -*-
from django.contrib.auth import get_user_model

from django.test import TestCase
from django_dynamic_fixture import G
from monitio import api, INFO


class messages:
    def __init__(self):
        self.messages = []

    def add(self, *args, **kw):
        self.messages.append((args, kw))


class PhonyRequest:
    def __init__(self):
        self._messages = messages()


class TestApi(TestCase):
    def setUp(self):
        self.request = PhonyRequest()

    def test_add_message(self):
        api.add_message(self.request, INFO, 'message', sse=False)

    def test_info(self):
        api.info(self.request, 'message')

    def test_warning(self):
        api.warning(self.request, 'warning')

    def test_debug(self):
        api.debug(self.request, 'debug')

    def test_create_message(self):
        api.create_message(
            G(get_user_model()), INFO, 'message')