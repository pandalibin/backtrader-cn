# -*- coding: utf-8 -*-
import backtradercn.datas.tushare as bdt
import backtradercn.tasks as btasks
import backtradercn.strategies.ma as bsm
import logging

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
    download_delta_data()
