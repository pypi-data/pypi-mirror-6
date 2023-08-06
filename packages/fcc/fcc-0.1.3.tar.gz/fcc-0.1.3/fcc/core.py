'''
Wrapers to provide error handling, exponential backoff and retry.
'''
from functools import wraps
import time

import logging
logger = logging.getLogger('fcc.core')


def exponential_backoff(base=6, max_attempts=3):
    '''
    Generally, set max_attempts to be one less than the number of attempts
    you actually want to make, because you'll try one more time after
    exponential_backoff is completed.
    '''
    for attempt in range(max_attempts):
        delay = base ** attempt
        yield delay
        time.sleep(delay)


def retry_on_exception(f):
    @wraps(f)
    def retrying(*args, **kwargs):
        for delay in exponential_backoff():
            try:
                return f(*args, **kwargs)
            except Exception as e:
                msg = 'Caught an Error: {0}. Retrying in {1} seconds. {2}'
                logging.warning(msg.format(e, delay, (args, kwargs)))
        return f(*args, **kwargs)
    return retrying


def retry_on_none(f):
    @wraps(f)
    def retrying(*args, **kwargs):
        for delay in exponential_backoff():
            value = f(*args, **kwargs)
            if value is not None:
                return value
            msg = 'Returned `None`. Retrying in {0} seconds.'
            logging.warning(msg.format(delay))
        return f(*args, **kwargs)
    return retrying
