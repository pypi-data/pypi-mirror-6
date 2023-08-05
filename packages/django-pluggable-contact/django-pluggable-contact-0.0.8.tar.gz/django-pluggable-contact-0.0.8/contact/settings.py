from django.conf import settings

# Minimum message length for contact forms and Message model
MIN_LENGTH = getattr(settings, 'CONTACT_MIN_MESSAGE_LENGTH', 10)

# Sender address for contact messages. Defaults to settings.DEFAULT_FROM_EMAIL.
SENDER = getattr(settings, 'CONTACT_SENDER', settings.DEFAULT_FROM_EMAIL)

# Default recipient for contact messages. Defaults to SENDER.
DEFAULT_RECIPIENT = getattr(settings, 'CONTACT_DEFAULT_RECIPIENT', SENDER)

# Simple mode. Disables access topics and selects SimpleContactForm for the
# contact view if True. Default is True.
SIMPLE = getattr(settings, 'CONTACT_SIMPLE', True)

# Whether to save messages in the database. Note that disabling this will still
# create the Message model and its database table.
DB_INBOX = getattr(settings, 'DB_INBOX', True)

# Override the form class for simple contact form. Set to ``None`` to use the
# default form.
SIMPLE_FORM_CLASS = getattr(settings, 'CONTACT_SIMPLE_FORM_CLASS', None)

# Override the form class for topic-based contact form. Set to ``None`` to use
# the default form.
TOPIC_FORM_CLASS = getattr(settings, 'CONTACT_TOPIC_FORM_CLASS', None)

# Whether to incldue topic admin section regardless of whether contact form is
# simple (since topics can still be used outside the contact form context).
# Default is oppoisite of SIMPLE.
TOPIC_ADMIN = getattr(settings, 'CONTACT_TOPIC_ADMIN', not SIMPLE)
