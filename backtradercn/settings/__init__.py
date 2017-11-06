# -*- coding: utf-8 -*-
import os
from backtradercn.settings import dev
from backtradercn.settings import test
from backtradercn.settings import prod
import logging


__all_ = ['settings']


settings = None

if os.environ.get('DEPLOY_ENV') == 'dev':
    settings = dev
elif os.environ.get('DEPLOY_ENV') == 'test':
    settings = test
elif os.environ.get('DEPLOY_ENV') == 'prod':
    settings = prod
else:
    # raise Exception('You must set the environment variable: `DEPLOY_ENV`'
    #                 'to one of ["dev", "test", "prod"]')

    log_format = '%(name)s:%(lineno)d %(levelname)s: %(message)s'
    logging.basicConfig(format=log_format)
    logger = logging.getLogger(__name__)
    logger.warning(
        'Do not set the environment variable: `DEPLOY_ENV`, '
        'using the default value: `dev`.'
    )
    settings = dev
