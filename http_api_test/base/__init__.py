import logging
import sys
from base import ini


def _get_logger():
    _logger = logging.getLogger('http_api_test')
    if ini.debug:
        _logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(stream=sys.stdout)
    else:
        _logger.setLevel(logging.INFO)
        log_dir = str(ini.logs_path)
        handler = logging.FileHandler(
            filename='{log_dir}/{name}.log'.format(log_dir=log_dir, name=ini.test_name),
            encoding='utf-8')

    handler.setFormatter(logging.Formatter(fmt='%(asctime)s <%(module)s.%(funcName)s> %(levelname)s: %(message)s',
                                           datefmt='%Y-%m-%d %H:%M:%S'))
    _logger.addHandler(handler)
    return _logger


logger = _get_logger()
props = dict()

__all__ = ['excel', 'result', 'ini', 'web_api', 'logger', 'props', 'mail']
