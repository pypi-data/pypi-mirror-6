# -*- encoding: utf-8 -*-
from datetime import timedelta, datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from django.test import TestCase
from django_dynamic_fixture import G, N
from monitio import INFO
from monitio.models import Monit
from monitio.storage import get_user, PersistentMessageStorage


class TestStorage(TestCase):
    def setUp(self):
        self.user = G(get_user_model())
        class req:
            user = self.user
            session = dict()
            COOKIES = dict()
        self.storage = PersistentMessageStorage(request=req)

    def test__message_queryset(self):
        m = G(Monit, read=False, user=self.user, expires=None)
        n = G(Monit, read=False, user=self.user, expires=datetime.now() - timedelta(days=1))
        res = list(self.storage._message_queryset(True))
        self.assertIn(m, res)
        self.assertNotIn(n, res)

        m.read = True
        m.save()
        res = self.storage._message_queryset(True)
        self.assertNotIn(m, list(res))

    def test__get_anonymous(self):
        self.user.is_authenticated = lambda foo=None: False
        self.assertEquals(self.storage._get(), ([], True))

    def test__get(self):
        m = G(Monit, read=False, user=self.user, expires=None)
        self.assertEquals(self.storage._get(), ([m], True))

    def test_get_persistent(self):
        m = G(Monit, read=False, user=self.user, expires=None, level=INFO)
        self.assertIn(m, self.storage.get_persistent())

        n = G(Monit, read=False, user=self.user, expires=None, level=31337)
        self.assertNotIn(n, self.storage.get_persistent())

    def test_get_persistent_unread(self):
        m = G(Monit, user=self.user, expires=None, level=INFO, read=False)
        n = G(Monit, user=self.user, expires=None, level=INFO, read=True)

        self.assertIn(m, self.storage.get_persistent_unread())
        self.assertNotIn(n, self.storage.get_persistent_unread())

    def test_get_nonpersistent(self):
        n = G(Monit, read=False, user=self.user, expires=None, level=31337)
        self.assertIn(n, self.storage.get_nonpersistent())

    def test_counts(self):
        self.assertEquals(0, self.storage.count_unread())
        self.assertEquals(0, self.storage.count_persistent_unread())
        self.assertEquals(0, self.storage.count_unread())

    def test__delete_non_persistent(self):
        n = G(Monit, read=False, user=self.user, expires=None, level=31337)
        self.storage.get_nonpersistent()
        self.storage._delete_non_persistent()
        self.assertEquals(Monit.objects.count(), 0)

    def test___iter__(self):
        m = G(Monit, read=False, user=self.user, expires=None, level=INFO)
        self.storage._queued_messages = ['bar']
        self.assertEquals(list(self.storage), [m, 'bar'])

    def test__store(self):
        m = N(Monit, read=False, user=self.user, expires=None, level=INFO)
        self.assertEquals(m.is_persistent(), True)
        self.assertEquals(Monit.objects.count(), 0)
        self.storage._store([m], 'response')
        self.assertEquals(Monit.objects.count(), 1)

    def test_update(self):
        self.storage.update('response')

    def test_add(self):
        self.storage.add(INFO, 'test')
        self.assertEquals(Monit.objects.count(), 1)



class TestStorageHelpers(TestCase):

    def test_get_user(self):
        class request:
            user = G(get_user_model())
        self.assertEquals(get_user(request), request.user)

    def test_get_user_anon(self):
        class request:
            user = AnonymousUser()
        self.assertEquals(get_user(request), AnonymousUser())

