from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from . import settings
from .email import send_html_email


def message_length(s):
    if not s: return
    if len(s) < settings.MIN_LENGTH:
        raise ValidationError(
            _('The message is too short. '
              'It must have at least %s characters.')
        )


class Topic(models.Model):
    name = models.CharField(
        _('name'),
        max_length=10,
        unique=True,
        help_text=_('Identifier, must be unique and up to 10 characters.')
    )
    display_name = models.CharField(
        _('display name'),
        max_length=40,
        unique=True,
        help_text='Unique label used in forms, up to 40 characters.'
    )
    default = models.BooleanField(
        _('default topic'),
        default=False,
        help_text='Default topics will receive messages when a message has no '
        'topic'
    )

    def message_count(self):
        return self.messages.count()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('topic')
        verbose_name_plural = _('topics')


class TopicInbox(models.Model):
    topic = models.ForeignKey(
        Topic,
        verbose_name=_('topic'),
        related_name='inboxes'
    )
    address = models.EmailField(
        _('email address'),

    )

    class Meta:
        verbose_name = _('topic inbox')
        verbose_name_plural = _('topic inboxes')


class Message(models.Model):
    topic = models.ForeignKey(
        Topic,
        verbose_name=_('topic'),
        related_name='messages',
        null=True,
        on_delete=models.SET_NULL
    )
    sender = models.EmailField(
        _('your email'),
        default=''
    )
    subject = models.CharField(
        _('subject'),
        max_length=100
    )
    body = models.TextField(
        _('message'),
        null=True,
        validators=[message_length]
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        editable=False
    )

    def send(self, template='contact/email/default.html', extra_context={},
             text_only=False, recipients=None, save=True, force_topic=False):

        if not recipients:
            if force_topic is False and settings.SIMPLE:
                recipients = settings.DEFAULT_RECIPIENT
            elif self.topic:
                # We have a topic, so send email to its inboxes
                recipients = [i.address for i in self.topic.inboxes.all()]
            else:
                # We don't have a message topic, so send to default topics
                # (if any)
                default_topics = Topic.objects.filter(default=True).all()
                recipients = [i.address for t in default_topics for i in t.inboxes]

        # Add this message object to extra context and use it as template
        # context
        context = extra_context
        context['message'] = self
        context['timestamp'] = timezone.now()

        # Send email
        send_html_email(
            subject=self.subject,
            from_email=settings.SENDER,
            to=recipients,
            template=template,
            data=context,
            reply_to=self.sender,
            text_only=text_only,
            send_separately=True
        )

        if settings.DB_INBOX and save:
            # If we are using DB_INBOX, save this message
            self.save()


    def __unicode__(self):
        return '%s from %s' % (
            self.subject,
            self.sender
        )

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')

