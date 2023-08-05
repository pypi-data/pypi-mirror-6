from django import forms

from .models import Message


class SimpleContactForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('sender', 'subject', 'body')


class TopicContactForm(forms.ModelForm):
    class Meta:
        model = Message

