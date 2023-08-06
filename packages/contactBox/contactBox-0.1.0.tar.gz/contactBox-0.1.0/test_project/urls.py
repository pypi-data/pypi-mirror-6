from django.contrib import admin
from django.conf import settings

from contactBox.views import ContactFormView
try:
    from django.conf.urls import patterns, url, include
except ImportError:
    from django.conf.urls.defaults import patterns, url

admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r"^contactBox/test_view/$", ContactFormView.as_view(), name="contact-box-form-test"),
    url(r"^admin/", include(admin.site.urls)),
    (r'^%s(?P<path>.*)$' % settings.STATIC_URL[1:],  # cut away leading slash
         'django.views.static.serve', {'document_root': settings.STATIC_ROOT,
                                       'show_indexes': True}),
    (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],  # cut away leading slash
         'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,
                                       'show_indexes': False}),)
