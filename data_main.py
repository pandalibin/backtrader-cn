# -*- coding: utf-8 -*-
import backtradercn.datas.tushare as bdt
import logging
import timeit

stock_pools = ['000651']


def download_delta_data():
    """
    Download delta data for all collections of all libraries.
    :return: None
    """
    # library: ts_his_data
    bdt.TsHisData.download_all_delta_data(*stock_pools)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    run_period = timeit.timeit('download_delta_data()',
                               setup='from __main__ import download_delta_data', number=1)

    logging.debug('Run period is %.2f seconds' % run_period)
