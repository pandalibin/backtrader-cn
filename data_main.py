# -*- coding: utf-8 -*-
import gevent.pool
import gevent.monkey
gevent.monkey.patch_all()

import tushare as ts
import backtradercn.datas.tushare as bdt
from backtradercn.libs.log import logging


logger = logging.getLogger(__name__)


def download_delta_data(stocks, pool_size=40):
    """
    Download delta data for all stocks collections of all libraries.
    :param stocks: stock code list.
    :param pool_size: the pool size of gevent.pool.Pool.
    :return: None
    """

    pool = gevent.pool.Pool(pool_size)
    for i in range(len(stocks) // pool_size + 1):
        start = i * pool_size
        end = (i + 1) * pool_size
        lst = stocks[start:end]
        logger.debug(f'fast download delta data for stock list: {lst}')
        for stock in lst:
            pool.spawn(bdt.TsHisData.download_one_delta_data, stock)
        pool.join(timeout=30)


if __name__ == '__main__':
    #download_delta_data(['000651'])

    top_hs300 = ts.get_hs300s()
    stock_pools = ts.get_hs300s()['code'].tolist() if 'code' in top_hs300 else []
    download_delta_data(stock_pools)
