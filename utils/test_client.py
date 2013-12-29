import requests

from django.core.urlresolvers import reverse

from readings.tests import ReadingFactory


def send_reading(domain):
    return requests.post(
        '%s%s' % (domain, reverse('readings-create-reading')), 
        data=ReadingFactory.attributes(),
    )
