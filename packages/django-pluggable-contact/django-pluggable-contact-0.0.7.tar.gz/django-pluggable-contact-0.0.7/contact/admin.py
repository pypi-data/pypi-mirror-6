from __future__ import unicode_literals

from django.contrib import admin

from .models import Topic, TopicInbox, Message
from .settings import SIMPLE


class TopicInboxesInline(admin.StackedInline):
    model = TopicInbox
    extra = 0


class TopicAdmin(admin.ModelAdmin):
    pass


if SIMPLE:
    message_admin_excludes = ('topic',)
else:
    message_admin_excludes = []


class MessageAdmin(admin.ModelAdmin):
    exclude = message_admin_excludes


if not SIMPLE:
    admin.site.register(Topic, TopicAdmin)

admin.site.register(Message, MessageAdmin)