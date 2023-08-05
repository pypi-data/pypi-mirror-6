# -*- encoding: utf-8 -*-

from django.test import TestCase
from django_dynamic_fixture import G
from monitio.models import Monit
from monitio.tasks import remove_read_messages


class TestTasks(TestCase):
    def setUp(self):
        self.m = G(Monit, read=True)
        pass

    def test_tasks(self):
        self.assertEquals(Monit.objects.all().count(), 1)
        remove_read_messages()
        self.assertEquals(Monit.objects.all().count(), 0)