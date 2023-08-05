from __future__ import unicode_literals

from django.views.generic import FormView, TemplateView
from django.core.urlresolvers import reverse

from .forms import SimpleContactForm, TopicContactForm, get_form_from_setting
from .settings import SIMPLE, DB_INBOX, SIMPLE_FORM_CLASS, TOPIC_FORM_CLASS

class ContactView(FormView):
    template_name = 'contact/contact.html'

    def get_form_class(self):
        if SIMPLE:
            if type(SIMPLE_FORM_CLASS) is str:
                return get_form_from_setting(SIMPLE_FORM_CLASS)
            else:
                return SIMPLE_FORM_CLASS or SimpleContactForm
        else:
            if type(TOPIC_FORM_CLASS) is str:
                return get_form_from_setting(TOPIC_FORM_CLASS)
            else:
                return TOPIC_FORM_CLASS or TopicContactForm

    def get_success_url(self):
        return reverse('thank_you')

    def send_message(self, message):
        # Send the message with default options
        message.send()

    def form_valid(self, form):
        # If DB_INBOX is set to False, do not commit to database
        message = form.save(commit=DB_INBOX)
        self.send_message(message)
        return super(ContactView, self).form_valid(form)


class ThankYouView(TemplateView):
    template_name = 'contact/thank_you.html'
