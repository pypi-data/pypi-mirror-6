sms-support
===========

Provides sms-support for data collection applications.

Quick start
-----------

1. Add "sms-support" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'sms-support',
    )

2. Include the sms-support URLconf in your projects urls.py like this::

    # SMS support
    url(r'^(?P<username>[^/]+)/', include('sms-support.urls'))
