from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from .views import ContactView, ThankYouView


urlpatterns = (
    '',
    url(_(r'^$'), ContactView.as_view(), name='contact'),
    url(_(r'^thank-you/$'), ThankYouView.as_view(), name='thank_you'),
)
