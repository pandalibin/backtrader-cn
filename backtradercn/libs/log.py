# -*- coding: utf-8 -*-
import os
import logging
from datetime import datetime
from logging.config import dictConfig
from backtradercn.settings import settings as conf


__all__ = ['getLogger']


LOG_PATH = os.path.join(
    conf.LOG_DIR,
    f'{datetime.now().strftime("%Y%m%d-%H%M%S-%f")}.log'
)

LOG_LEVEL = conf.LOG_LEVEL
# overwrite `LOG_LEVEL` via set environment variable
LOG_LEVEL = os.getenv('LOG_LEVEL', LOG_LEVEL).upper()

LOG_LEVELS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
if LOG_LEVEL not in LOG_LEVELS:
    logging.warning(
        f'Please set the correct value for `LOG_LEVEL`, current value: {LOG_LEVEL}'
    )
    logging.warning('Using the default `LOG_LEVEL`: `DEBUG`')
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.getLevelName(LOG_LEVEL)

logging_config = dict(
    version=1,
    formatters={
        'standard': {
            'format':
            '%(asctime)s %(name)s:%(lineno)d %(levelname)s: %(message)s',
            'default_msec_format': '%s.%03d',
            'converter': 'time.gmtime'
        }
    },
    handlers={
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': LOG_LEVEL,
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'standard',
            'level': LOG_LEVEL,
            'filename': LOG_PATH,
            'mode': 'a',
        }
    },
    root={
        'handlers': ['console', 'file'],
        'level': LOG_LEVEL,
    },
)

dictConfig(logging_config)

# replace comma with period
# e.g.: 2010-09-06 22:38:15,292 => 2010-09-06 22:38:15.292
for h in logging.getLogger().handlers:
    h.formatter.default_msec_format = '%s.%03d'


def getLogger(name=None):
    return logging.getLogger(name)
