# -*- encoding: utf-8 -*-

from django.test import TestCase
from monitio.constants import INFO
from monitio.models import Monit


class TestModels(TestCase):
    def test___unicode__(self):
        m = Monit(message='foo')
        self.assertEquals(unicode(m), u'foo')

        m = Monit(message='foo', subject='bar')
        self.assertEquals(unicode(m), u'bar: foo')

    def test__prepare_message(self):
        m = Monit(subject='foo', message='bar', extra_tags='baz')
        m._prepare_message()

    def test_save(self):
        m = Monit(subject='foo', message='bar', extra_tags='baz', level=INFO)
        m.save()

    def test__get_tags(self):
        m = Monit(extra_tags="foo", level=INFO)
        self.assertEquals(m._get_tags(), ['foo', 'info', 'unread'])

        m.read = True
        self.assertEquals(m._get_tags(), ['foo', 'info', 'read'])

        m.extra_tags = None
        self.assertEquals(m._get_tags(), ['info', 'read'])

        m.level = None
        self.assertEquals(m._get_tags(), ['read'])
