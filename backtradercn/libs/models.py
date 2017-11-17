# -*- coding: utf-8 -*-
import arctic
from backtradercn.libs.log import getLogger
from backtradercn.settings import settings as conf


logger = getLogger(__name__)


def get_store():
    mongo_host = conf.MONGO_HOST
    store = arctic.Arctic(mongo_host)
    return store


def create_library(lib_name):
    store = get_store()
    if lib_name not in store.list_libraries():
        logger.info(f'initialize library: {lib_name}')
        store.initialize_library(lib_name)
    else:
        logger.warning(f'library: {lib_name} exist, skip.')

    return store[lib_name]


def drop_library(lib_name):
    store = get_store()
    if lib_name in store.list_libraries():
        logger.info(f'drop library: {lib_name}')
        store.delete_library(lib_name)
    else:
        logger.warning(f'can not find library: {lib_name}')
