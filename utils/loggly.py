import datetime
import logging

from django.utils import simplejson as json


loggly_logger = logging.getLogger('loggly')

def loggly(**kwargs):
    print kwargs
    msg = {
        'timestamp': datetime.datetime.utcnow().isoformat(),
    }
    msg.update(**kwargs)
    loggly_logger.info(json.dumps(msg))


class Logger(object):

    def log(self, **kwargs):
        kwargs.update({
            'view': type(self).__name__,
        })
        loggly(**kwargs)
