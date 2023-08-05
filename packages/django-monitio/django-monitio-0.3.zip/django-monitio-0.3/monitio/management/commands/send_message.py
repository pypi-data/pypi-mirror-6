import sys

from django.core.management.base import BaseCommand

from django.contrib import auth

User = auth.get_user_model()

from monitio import api


def err(msg, status=-1):
    sys.stderr.write('%s: %s\n' % (sys.argv[0], msg))
    sys.exit(status)


def get_user(username):
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        err("No such user: %r" % username)


class Command(BaseCommand):
    args = 'from_user to_user message'
    help = '''This tool creates a persistent message in the database.

    Usage: send_message [from user] [to user] [level=INFO,ERROR,DEBUG...] [message]'''

    def handle(self, *args, **options):
        try:
            from_user, to_user = [get_user(username) for username in args[:2]]
        except ValueError:
            err(self.help)

        message = " ".join(args[3:])
        level = getattr(api.constants, args[2])
        api.create_message(level=level,
                           from_user=from_user, to_user=to_user,
                           message=message,
                           subject="%s message" % args[2],
                           sse=True)
