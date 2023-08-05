# -*- encoding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404

from django.test import TestCase, RequestFactory
from django_dynamic_fixture import G
from monitio.models import Monit
from monitio.templatetags.mark_as_read_by_url import mark_as_read_by_url
from monitio.views import message_detail, message_delete, message_delete_all, message_mark_read, message_mark_all_read, DynamicChannelRedisQueueView, SameUserChannelRedisQueueView


User = get_user_model()


class UserRequestFactory(RequestFactory):
    def __init__(self, user, *args, **kw):
        self.user = user
        super(UserRequestFactory, self).__init__(*args, **kw)

    def get(self, *args, **kw):
        req = super(UserRequestFactory, self).get(*args, **kw)
        req.user = self.user
        return req


class TestViews(TestCase):
    def setUp(self):
        self.user = G(User)
        self.factory = UserRequestFactory(self.user)
        self.message = G(Monit, read=False, message='foo', user=self.user)
        self.request = self.factory.get("/")

    def reload(self):
        self.message = Monit.objects.get(pk=self.message.pk)

    def assertRead(self):
        self.reload()
        self.assertEquals(self.message.read, True)

    def assertDeleted(self):
        self.assertEquals(Monit.objects.count(), 0)

    def assertUnread(self):
        self.reload()
        self.assertEquals(self.message.read, False)

    def assert404(self, method):
        self.assertRaises(Http404, method, self.request, -1)

    def non_ajax_request(self):
        self.request.META['HTTP_REFERER'] = 'foo'

    def assertNonAjaxRequestOkay(self, res):
        self.assertEquals(res._headers['location'][1], 'foo')
        self.assertContains(res, '', status_code=302)

    def ajax_request(self):
        self.request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'

    def assertAjaxRequestOkay(self, res):
        self.assertContains(res, '', status_code=200)

    def user_not_authenticated(self):
        self.request.user.is_authenticated = lambda self=None: False

    def test_message_delete(self):
        self.assert404(message_delete)

        self.non_ajax_request()
        res = message_delete(self.request, self.message.pk)
        self.assertNonAjaxRequestOkay(res)

    def test_message_delete_ajax(self):
        self.ajax_request()
        res = message_delete(self.request, self.message.pk)
        self.assertAjaxRequestOkay(res)

    def assertPermissionDenied(self, fun):
        self.user_not_authenticated()
        self.assertRaises(PermissionDenied, fun, self.request)

    def test_message_delete_all_permission(self):
        self.assertPermissionDenied(message_delete_all)

    def test_message_delete_all(self):
        extra = G(Monit, user=G(User))
        self.assertEquals(Monit.objects.count(), 2)

        self.non_ajax_request()
        res = message_delete_all(self.request)

        self.assertEquals(Monit.objects.count(), 1)
        self.assertNonAjaxRequestOkay(res)

    def test_message_delete_all_ajax(self):
        self.ajax_request()
        self.assertAjaxRequestOkay(message_delete_all(self.request))

    def test_message_mark_read_permission(self):
        self.user_not_authenticated()
        self.assertRaises(PermissionDenied, message_mark_read, self.request,
                          self.message.pk)

    def test_mark_read(self):
        self.assert404(message_mark_read)

        self.assertUnread()
        self.non_ajax_request()
        res = message_mark_read(self.request, self.message.pk)
        self.assertNonAjaxRequestOkay(res)
        self.assertRead()

    def test_mark_read_ajax(self):
        self.ajax_request()
        self.assertAjaxRequestOkay(
            message_mark_read(self.request, self.message.pk))

    def test_message_mark_all_read(self):
        m1 = G(Monit, user=G(User), read=False)
        m2 = G(Monit, user=self.user, read=False)
        self.assertUnread()

        res = message_mark_all_read(self.request)
        self.assertRead()
        self.assertEquals(Monit.objects.get(pk=m1.pk).read, False)
        self.assertEquals(Monit.objects.get(pk=m2.pk).read, True)

    def test_message_mark_all_read_non_ajax(self):
        self.non_ajax_request()
        self.assertNonAjaxRequestOkay(
            message_mark_all_read(self.request))

    def test_message_mark_all_ajax(self):
        self.ajax_request()
        self.assertAjaxRequestOkay(message_mark_all_read(self.request))

    def test_message_mark_all_read_permission(self):
        self.assertPermissionDenied(message_mark_all_read)

    def test_dynamic_channel_redis_queue_view(self):
        d = DynamicChannelRedisQueueView()
        d.kwargs = dict(channel='foo')
        self.assertEquals(d.get_redis_channel(), 'foo')

        d = DynamicChannelRedisQueueView()
        d.kwargs = dict()
        d.redis_channel = 'bar'
        self.assertEquals(d.get_redis_channel(), 'bar')

    def test_same_user_channel_redis_queue_view(self):
        s = SameUserChannelRedisQueueView()

        backup = DynamicChannelRedisQueueView.dispatch

        try:
            DynamicChannelRedisQueueView.dispatch = lambda *args, **kw: True

            # Anonymous access enabled by default
            self.user.is_anonymous = lambda self=None: True
            self.assertEquals(s.dispatch(self.request), True)

            # Logged-in access for users, who have same username as channel name
            self.user.is_anonymous = lambda self=None: False
            self.assertEquals(s.dispatch(self.request).status_code, 403)

            s.redis_channel = self.user.username
            self.assertEquals(s.dispatch(self.request), True)

        finally:
            DynamicChannelRedisQueueView.dispatch = backup


URL = "/omg/roxx/"
URL_2 = URL + "/foo"

class TestMarkAsRead(TestCase):
    def setUp(self):
        self.user = G(User)
        self.user_2 = G(User)
        self.factory = UserRequestFactory(self.user)
        self.message = G(
            Monit, read=False, message='foo', user=self.user, url=URL)
        self.message = G(
            Monit, read=False, message='foo', user=self.user, url=URL_2)
        self.message = G(
            Monit, read=False, message='foo', user=self.user_2, url=URL)
        self.request = self.factory.get(URL)

    def test_mark_as_read_by_url(self):
        context = dict(request=self.request)
        mark_as_read_by_url(context)
        self.assertEquals(
            Monit.objects.get(url=URL, user=self.user).read, True)
        self.assertEquals(
            Monit.objects.get(url=URL_2, user=self.user).read, False)
        self.assertEquals(
            Monit.objects.get(url=URL, user=self.user_2).read, False)
