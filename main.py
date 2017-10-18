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


def back_test():
    """
    Run back testing tasks via multiprocessing
    :return: None
    """
    for stock in stock_pools:
        task = btasks.Task(bsm.MATrendStrategy, stock)
        result = task.task()
        logging.debug(
            'Back testing result, trading days: %.2f, total return rate: %.2f, max drawdown: %.2f, max drawdown period: %.2f'
            % (result.get('trading_days'),
               result.get('total_return_rate'),
               result.get('max_drawdown'),
               result.get('max_drawdown_period')))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # download_delta_data()
    back_test()
