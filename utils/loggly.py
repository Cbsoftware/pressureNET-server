import datetime
import logging

from django.utils import simplejson as json


loggly_logger = logging.getLogger('loggly')

def loggly(**kwargs):
    msg = {
        'timestamp': datetime.datetime.utcnow().isoformat(),
    }
    msg.update(**kwargs)
    loggly_logger.info(json.dumps(msg))
