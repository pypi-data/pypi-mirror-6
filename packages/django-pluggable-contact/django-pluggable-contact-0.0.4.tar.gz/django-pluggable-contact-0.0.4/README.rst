========================
django-pluggable-contact
========================

Pluggable Django app for contact forms with database-based inbox and support for
topic-based sorting and sending to multiple recipients based on topic. Fully
i18n-enabled and supports South migrations. It supports HTML emails and
automatic conversion of HTML email to plain-text.

Overview
========

django-pluggable-contact should be fairly flexible. It is designed to be able
to handle anything from a very simple contact form to scenarios where you may
want to send different messages to different recipients.

Although it uses the Message models to store messages in the database, it is
optional. You can send out a message even if the object is not saved. Topics are
also optional. If you don't want the complexity of topics, you can disable them
completely and they won't show up in the admin or the contact form.

While more features will be added to this app as time goes, the overhead of
additional features will be kept to minimum or eliminated by using appropriate
settings for enabling them and having them disabled by default. On the other
hand, this app will always be just a contacts app.

TODO
====

1. Better docs

2. Unit tests

3. Add support for configuring multiple email accounts

Installation
============

TODO

Add the ``contact`` app to ``INSTALLED_APPS`` and call the syncdb management
command or migrate using South.

Map the URLs like so::

    url(r'^contact/', include('contact.urls'))

You can also include the URL in i18n_patterns as the URLs are fully
translatable.

Basic usage
===========

At very least, you want to override the provided basic templates. Please look
at the ``contact/templates`` directory.

Settings
========

TODO
