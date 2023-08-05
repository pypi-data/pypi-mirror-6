from django.conf.urls import patterns, url

from sms_support import providers, views


urlpatterns = patterns(
    url(r'forms/(?P<id_string>[^/]+)/sms_submission/(?P<service>[a-z]+)/?$',
        providers.import_submission_for_form, name='sms_submission_form_api'),
    url(r'forms/(?P<id_string>[^/]+)/sms_submission$',
        views.import_submission_for_form, name='sms_submission_form'),
    url(r"sms_submission/(?P<service>[a-z]+)/?$", providers.import_submission,
        name='sms_submission_api'),
    url(r'forms/(?P<id_string>[^/]+)/sms_multiple_submissions$',
        views.import_multiple_submissions_for_form,
        name='sms_submissions_form'),
    url(r"sms_multiple_submissions$", views.import_multiple_submissions,
        name='sms_submissions'),
    url(r"sms_submission$", views.import_submission, name='sms_submission'))
