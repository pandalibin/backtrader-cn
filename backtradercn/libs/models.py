# -*- coding: utf-8 -*-
import arctic
import pandas as pd
from backtradercn.libs.log import getLogger
from backtradercn.settings import settings as conf


logger = getLogger(__name__)


def get_store():
    """
    get Arctic store connection
    :return: arctic connection
    """

    mongo_host = conf.MONGO_HOST
    store = arctic.Arctic(mongo_host)
    return store


def get_library(lib_name):
    """
    get library by name
    :param lib_name: str, library name
    :return: arctic library object
    """

    store = get_store()

    lib = None
    if lib_name not in store.list_libraries():
        logger.debug(f'can not find library: {lib_name}.')
    else:
        lib = store.get_library(lib_name)

    return lib


def create_library(lib_name):
    """
    create library with name: `lib_name`
    :param lib_name: str, library name
    :return: arctic library object
    """

    store = get_store()
    if lib_name not in store.list_libraries():
        logger.info(f'initialize library: {lib_name}')
        try:
            store.initialize_library(lib_name)
        except Exception as e:
            logger.error(f'initialize library failed: {e}', exc_info=True)
    else:
        logger.debug(f'library: {lib_name} exist, skip.')

    return store.get_library(lib_name)


def get_or_create_library(lib_name):
    """
    get library by `lib_name`, if not exists, then create it.
    :param lib_name: str, library name
    :return: arctic library object
    """

    lib = get_library(lib_name)
    if not lib:
        lib = create_library(lib_name)

    return lib


def drop_library(lib_name):
    """
    drop library by name: `lib_name`
    :param lib_name: str, library name
    :return: None
    """

    store = get_store()
    if lib_name in store.list_libraries():
        logger.info(f'drop library: {lib_name}')
        store.delete_library(lib_name)
    else:
        logger.warning(f'can not find library: {lib_name}')


def get_cn_stocks():
    """
    get all chinese stock ids from arctic library.
    :return: list, stock id list. e.g.: ['000651', '601988' ...]
    """

    lib = get_library(conf.CN_STOCK_LIBNAME)
    return lib.list_symbols()


def save_training_params(symbol, params):
    """
    save training params to library.
    :param symbol: str, arctic symbol
    :param params: dict, e.g.: {"ma_period_s": 1, "ma_period_l": 2, "stock_id": "600909"}
    :return: None
    """

    stock_id = params.ma_periods['stock_id']
    params_to_save = dict(params=params)
    df = pd.DataFrame([params_to_save], columns=params_to_save.keys(), index=[stock_id])

    # write to database
    # if library does not exist, create it
    lib = get_or_create_library(conf.STRATEGY_PARAMS_LIBNAME)

    if lib.has_symbol(symbol):
        logger.debug(
            f'symbol: {symbol} already exists, '
            f'change the params of stock {stock_id}, '
            f'then delete and write symbol: {symbol}.'
        )
        params_df = lib.read(symbol).data
        params_df.loc[stock_id, 'params'] = params
        lib.delete(symbol)
        lib.write(symbol, params_df)
    else:
        logger.debug(
            f'write the params of stock {stock_id} to symbol: {symbol}'
        )
        lib.write(symbol, df)
