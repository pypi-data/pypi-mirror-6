from django import forms

from .models import Message

def get_form_from_setting(setting):
    # This is a rather ugly way to import something, but too lazy to look for a
    # better approach. For now this works.
    components = setting.split('.')
    module = '.'.join(components[:-1])
    name = components.pop()
    print module, name
    return getattr(__import__(module, globals(), locals(), [name], -1), name)


class SimpleContactForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('sender', 'subject', 'body')


class TopicContactForm(forms.ModelForm):
    class Meta:
        model = Message

