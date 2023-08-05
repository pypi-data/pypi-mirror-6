from django.conf.urls import patterns, url


urlpatterns = patterns(
    url(r'forms/(?P<id_string>[^/]+)/sms_submission/(?P<service>[a-z]+)/?$',
        'sms_support.providers.import_submission_for_form',
        name='sms_submission_form_api'),
    url(r'forms/(?P<id_string>[^/]+)/sms_submission$',
        'sms_support.views.import_submission_for_form',
        name='sms_submission_form'),
    url(r"sms_submission/(?P<service>[a-z]+)/?$",
        'sms_support.providers.import_submission',
        name='sms_submission_api'),
    url(r'forms/(?P<id_string>[^/]+)/sms_multiple_submissions$',
        'sms_support.views.import_multiple_submissions_for_form',
        name='sms_submissions_form'),
    url(r"sms_multiple_submissions$",
        'sms_support.views.import_multiple_submissions',
        name='sms_submissions'),
    url(r"sms_submission$",
        'sms_support.views.import_submission', name='sms_submission'))
