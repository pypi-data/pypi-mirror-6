import datetime

from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django_transaction_signals import defer
from monitio import notify

from monitio.models import Monit
from monitio.constants import PERSISTENT_MESSAGE_LEVELS


def get_user(request):
    if hasattr(request, 'user') and request.user.__class__ != AnonymousUser:
        return request.user
    else:
        return AnonymousUser()

"""
Messages need a primary key when being displayed so that they can be closed/marked as read by the user.
Hence, they need to be stored when being added. You can disable this, but then you'll only be able to 
close a message when it is displayed for the second time. 
"""
STORE_WHEN_ADDING = True

#TODO: USE FALLBACK 
class PersistentMessageStorage(FallbackStorage):
    def __init__(self, *args, **kwargs):
        """
        Inherited attributes:
            self.request = request
            self._queued_messages = []
            self.used = False
            self.added_new = False
        """
        super(PersistentMessageStorage, self).__init__(*args, **kwargs)
        self.non_persistent_messages = []

    def _message_queryset(self, exclude_read=None):
        """
        Gets the messages from the model. If `exclude_unread` is set to True, read messages are excluded
        """
        qs = Monit.objects.filter(user=get_user(self.request)).filter(
            Q(expires=None) | Q(expires__gt=datetime.datetime.now()))

        # If the function didn't get an exclude_read argument, we look for it in settings
        if exclude_read is None:
            # By default read messages are not excluded, we show all messages
            exclude_read = getattr(settings, 'MONITIO_EXCLUDE_READ', False)

        if exclude_read:
            qs = qs.exclude(read=True)

        return qs

    def _get(self, *args, **kwargs):
        """
        Retrieves a list of stored messages. Returns a tuple of the messages
        and a flag indicating whether or not all the messages originally
        intended to be stored in this storage were, in fact, stored and
        retrieved: `(messages, all_retrieved)`

        This is called by BaseStorage._loaded_messages
        """

        is_anonymous = not get_user(self.request).is_authenticated()
        if is_anonymous:
            return super(PersistentMessageStorage, self)._get(*args, **kwargs)

        messages = []
        for message in self._message_queryset():
            if not message.is_persistent():
                self.non_persistent_messages.append(message)
            messages.append(message)
        return (messages, True)

    def get_persistent(self):
        """
        Get read and unread persistent messages
        """
        return self._message_queryset(exclude_read=False).filter(
            level__in=PERSISTENT_MESSAGE_LEVELS)

    def get_persistent_unread(self):
        """
        Get unread persistent messages
        """
        return self._message_queryset(exclude_read=True).filter(
            level__in=PERSISTENT_MESSAGE_LEVELS)

    def get_nonpersistent(self):
        """
        Gets nonpersistent messages, loads `self.non_persistent_messages` and sets `self.used` to `True`
        so that the middleware deletes them when calling `update` method
        """
        nonpersistent_messages = self._message_queryset(
            exclude_read=False).exclude(level__in=PERSISTENT_MESSAGE_LEVELS)

        self.non_persistent_messages = [message for message in
                                        nonpersistent_messages]
        self.used = True

        return nonpersistent_messages

    def count_unread(self):
        """
        Counts persistent and nonpersistent unread messages
        """
        return self._message_queryset(exclude_read=True).count()

    def count_persistent_unread(self):
        """
        Counts persistent unread messages
        """
        return self.get_persistent_unread().count()

    def count_nonpersistent(self):
        """
        Counts nonpersistent messages
        """
        return self._message_queryset(exclude_read=False).exclude(
            level__in=PERSISTENT_MESSAGE_LEVELS).count()

    def _delete_non_persistent(self):
        """
        Deletes nonpersistent messages stored in `self.non_persistent_messages` list.
        The list contains `Message` objects stored in the DB with a nonpersistent level,
        thus we need to iterate the list deleting them.
        """
        for message in self.non_persistent_messages:
            message.delete()
        self.non_persistent_messages = []

    def __iter__(self):
        is_anonymous = not get_user(self.request).is_authenticated()
        if is_anonymous:
            return super(PersistentMessageStorage, self).__iter__()

        self.used = True
        messages = []
        messages.extend(self._loaded_messages)
        if self._queued_messages:
            messages.extend(self._queued_messages)
        return iter(messages)

    def _prepare_messages(self, messages):
        """
        Obsolete method since model takes care of this.
        """
        is_anonymous = not get_user(self.request).is_authenticated()
        if is_anonymous:
            return super(PersistentMessageStorage, self)._prepare_messages(
                messages)
        pass

    def _store(self, messages, response, *args, **kwargs):
        """
        Stores a list of messages, returning a list of any messages which could
        not be stored.

        If STORE_WHEN_ADDING is True, messages are already stored at this time and won't be
        saved again.
        """
        is_anonymous = not get_user(self.request).is_authenticated()
        if is_anonymous:
            return super(PersistentMessageStorage, self)._store(messages,
                                                                response, *args,
                                                                **kwargs)

        for message in messages:
            if not self.used or message.is_persistent():
                if not message.pk:
                    message.save()
        return []

    def update(self, response):
        """
        Deletes all nonpersistent read messages and saves all unstored messages.

        This method is called by `process_response` in messages middleware
        """
        is_anonymous = not get_user(self.request).is_authenticated()
        if is_anonymous:
            return super(PersistentMessageStorage, self).update(response)

        if self.used:
            self._delete_non_persistent()

        return super(PersistentMessageStorage, self).update(response)

    @transaction.atomic
    def add(self, level, message, extra_tags='', subject='', user=None,
            from_user=None, expires=None, close_timeout=None,
            sse=False, email=False, url=None):
        """
        Adds or queues a message to the storage

        :param level: Level of the message
        :param message: Message text to be saved
        :param extra_tags: String with separated tags to add to message Ex: "secret classified"
        :param subject: Subject of the message 
        :param user: `auth.User` that receives the message
        :param from_user: `auth.User` that sends the message
        :param expires: Timestamp that indicates when the message expires
        :param close_timeout: Integer
        :param url: Optional string with URL leading to details of a given message

        .. note:: The message is only saved if it contains something and its level is over the recorded level (`MESSAGE_LEVEL`) `self.level`
        """
        to_user = user or get_user(self.request)
        if not to_user.is_authenticated():
            if Monit(level=level).is_persistent():
                raise NotImplementedError(
                    'Persistent message levels cannot be used for anonymous users.')
            else:
                return super(PersistentMessageStorage, self).add(level, message,
                                                                 extra_tags)
        if not message:
            return

        # Save the message only if its level is over the recorded level, see `MESSAGE_LEVEL` in Django docs
        level = int(level)
        if level < self.level:
            return

        # Add the message
        message = Monit(user=to_user, level=level, message=message,
                        extra_tags=extra_tags, subject=subject,
                        from_user=from_user, expires=expires,
                        close_timeout=close_timeout, url=url)

        # Messages need a primary key when being displayed so that they can be
        # closed/marked as read by the user. Hence, save it now instead of
        # adding it to queue:
        if STORE_WHEN_ADDING:
            message.save()

            if sse:
                # Sent delayed SSE notification
                defer(notify.via_sse, message.pk)

            if email:
                defer(notify.via_email, message.pk)

            return message
        else:
            self.added_new = True
            self._queued_messages.append(message)
