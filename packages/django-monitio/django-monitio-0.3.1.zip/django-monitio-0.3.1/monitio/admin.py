from monitio.models import Monit
from django.contrib import admin


class MessageAdmin(admin.ModelAdmin):
    list_display = ['level', 'user', 'from_user', 'subject', 'message',
                    'created', 'read', 'is_persistent']


admin.site.register(Monit, MessageAdmin)
