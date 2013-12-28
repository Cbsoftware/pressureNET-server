import requests

from django.core.urlresolvers import reverse

from readings.tests import ReadingFactory


def send_reading(domain):
    post_data = ReadingFactory.attributes()
    del post_data['date']

    return requests.post(
        '%s%s' % (domain, reverse('readings-create-reading')), 
        data=post_data
    )
