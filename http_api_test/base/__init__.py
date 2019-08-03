import logging
from pathlib import Path
import time
import sys

_DEBUG = False


def _get_logger():
    _logger = logging.getLogger('http_api_test')
    _logger.setLevel(logging.DEBUG)
    if _DEBUG:
        handler = logging.StreamHandler(stream=sys.stdout)
    else:
        log_dir = str(Path(__file__).resolve().parents[1] / 'logs')
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
