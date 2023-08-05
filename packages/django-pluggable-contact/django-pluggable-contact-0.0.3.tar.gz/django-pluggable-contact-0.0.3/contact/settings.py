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

