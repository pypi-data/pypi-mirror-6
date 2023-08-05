# -*- encoding: utf-8 -*-
from django.core import mail

from django.test import TestCase
from monitio import notify


class TestNotify(TestCase):
    def test_email_raises(self):
        def test_raises(user):
            self.assertRaises(
                Exception,
                notify.email, 'level', 'message', 'tags', 'subject', user,
                'from')

        test_raises(None)

        class user:
            email = None

        test_raises(user)

    def test_email_sends(self):
        class user:
            email = 'foo@127.0.0.1'

        notify.email('UNUSED', 'message', 'tags', 'subject', user, None)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, 'subject')

    def test_sse(self):
        backup = notify.send_event

        try:
            notify.send_event = lambda *args, **kw: [args, kw]

            res = notify.sse('level', 'pk', 'message', 'extra_tags', 'subject',
                             'user', 'from_user')

        finally:
            notify.send_event = backup