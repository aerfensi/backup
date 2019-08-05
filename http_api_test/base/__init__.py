import logging
import time
import sys
from base import ini


def _get_logger():
    _logger = logging.getLogger('http_api_test')
    if ini.DEBUG:
        _logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(stream=sys.stdout)
    else:
        _logger.setLevel(logging.INFO)
        log_dir = str(ini.LOGS_PATH)
        handler = logging.FileHandler(
            filename='{log_dir}/{name}.logs'.format(log_dir=log_dir,
                                                    name='TestResults__' + time.strftime('%Y-%m-%d_%H-%M-%S')),
            encoding='utf-8')

    handler.setFormatter(logging.Formatter(fmt='%(asctime)s <%(module)s.%(funcName)s> %(levelname)s: %(message)s',
                                           datefmt='%Y-%m-%d %H:%M:%S'))
    _logger.addHandler(handler)
    return _logger


logger = _get_logger()
props = dict()

__all__ = ['excel', 'result', 'ini', 'web_api', 'logger', 'props']
