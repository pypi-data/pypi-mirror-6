from django.conf.urls import patterns, url
from django.views.i18n import javascript_catalog
from monitio.views import SameUserChannelRedisQueueView

js_info_dict = {
    'domain': 'djangojs',
    'packages': ('monitio',),
}
urlpatterns = patterns(
    'monitio.views',
    url(r'^detail/(?P<message_id>\d+)/$', 'message_detail',
        name='message_detail'),

    # Mark read
    url(r'^mark_read/(?P<message_id>\d+)/$', 'message_mark_read',
        name='message_mark_read'),
    url(r'^mark_read/all/$', 'message_mark_all_read',
        name='message_mark_all_read'),

    # Delete
    url(r'^delete/message/(?P<message_id>\d+)/$', 'message_delete',
        name='message_delete'),
    url(r'^delete/all/$', 'message_delete_all', name='message_delete_all'),

    # Get via json
    url(r'^json/$', 'messages_json', name='message_json'),

    # django-sse
    url(r'^sse/(?P<channel>\w+)?$',
        SameUserChannelRedisQueueView.as_view(), name="persistent-messages-sse"),

    # i18n
    url(r'^jsi18n/$',
        javascript_catalog, # 'django.views.i18n.javascript_catalog',
        js_info_dict,
        name="js_i18n"),

)
