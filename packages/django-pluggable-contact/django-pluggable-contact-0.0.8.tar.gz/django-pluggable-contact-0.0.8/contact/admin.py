from __future__ import unicode_literals

from django.contrib import admin

from .models import Topic, TopicInbox, Message
from .settings import SIMPLE, TOPIC_ADMIN


class TopicInboxesInline(admin.StackedInline):
    model = TopicInbox
    extra = 0


class TopicAdmin(admin.ModelAdmin):
    inlines = [TopicInboxesInline]
    list_display = (
        'name',
        'display_name',
        'default',
        'subscribers',
    )
    list_editable = (
        'default',
    )


class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'sender',
        'subject',
        'created_at',
    ]
    list_filter = [
        'created_at'
    ]
    search_fields = [
        'sender',
        'subject',
        'body'
    ]

if (not SIMPLE) or TOPIC_ADMIN:
    admin.site.register(Topic, TopicAdmin)
    MessageAdmin.list_display.append('topic')
    MessageAdmin.list_filter.append('topic')
    MessageAdmin.exclude = ('topic',)

admin.site.register(Message, MessageAdmin)
