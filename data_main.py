# -*- coding: utf-8 -*-
import gevent.monkey
gevent.monkey.patch_all()

import tushare as ts
import backtradercn.datas.tushare as bdt
from backtradercn.config.log import logging
import gevent.pool


logger = logging.getLogger(__name__)
# stock_pools = ['000651']
top_hs300 = ts.get_hs300s()
stock_pools = ts.get_hs300s()['code'].tolist() if 'code' in top_hs300 else []


def download_delta_data():
    """
    Download delta data for all collections of all libraries.
    :return: None
    """
    # library: ts_his_data
    bdt.TsHisData.download_all_delta_data(*stock_pools)


def fast_download_delta_data(stocks, pool_size=20):
    length = len(stocks)
    pool = gevent.pool.Pool(pool_size)
    for i in range(int(length / pool_size) + 1):
        start = i * pool_size
        end = (i + 1) * pool_size
        lst = stocks[start:end]
        logger.debug(f'fast download delta data for stock list: {lst}')
        for stock in lst:
            pool.spawn(bdt.TsHisData.download_one_delta_data, stock)
        pool.join(timeout=30)


if __name__ == '__main__':
    # download_delta_data()
    fast_download_delta_data(stock_pools)
