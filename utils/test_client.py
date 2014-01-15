import requests
import time

from django.core.urlresolvers import reverse

from readings.tests import ReadingFactory


def send_reading(domain, data=None):
    data = data or ReadingFactory.attributes()
    return requests.post(
        '%s%s' % (domain, reverse('readings-create-reading')),
        data=data,
    )


def upload_readings(reading_file, url):
    start = time.time()
    count = 0
    while 1:
        line = reading_file.readline()

        tokens = line.split('\t')
        if not len(tokens) == 11:
            continue

        fields = (
            'id',
            'latitude',
            'longitude',
            'daterecorded',
            'reading',
            'tzoffset',
            'user_id',
            'sharing',
            'client_key',
            'location_accuracy',
            'reading_accuracy',
        )

        data = {}
        for field, value in zip(fields, tokens):
            if '.' in value:
                try:
                    value = float(value)
                except:
                    pass
            else:
                try:
                    value = int(value)
                except:
                    pass

            data[field] = value

        del data['id']
        data['altitude'] = 0
        data['observation_unit'] = 'mbars'
        data['observation_type'] = 'pressure'
        data['provider'] = 'network'

        send_reading(url, data=data)
        count += 1
        rate = (time.time() - start) / float(count)
        print '%s/s sending %s' % (rate, data)
