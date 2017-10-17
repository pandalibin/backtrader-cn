# -*- coding: utf-8 -*-
import backtradercn.datas.tushare as bdt
import backtradercn.tasks as btasks
import backtradercn.strategies.ma as bsm
import multiprocessing
import logging

stock_pools = ['000651']


def download_delta_data():
    """
    Download delta data for all collections of all libraries.
    :return: None
    """
    # library: ts_his_data
    bdt.TsHisData.download_all_delta_data(*stock_pools)


def run_back_tesing():
    """
    Run back testing tasks via multiprocessing
    :return: None
    """
    # pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    # results = []
    #
    # for stock in stock_pools:
    #     task = btasks.Task(bsm.MATrendStrategy, stock)
    #     results.append(pool.apply_async(task.task))
    #
    # pool.close()
    # pool.join()
    #
    # for result in results:
    #     logging.info('total return rate: %.2f, max drawdown: %.2f, max drawdown period: %.2f'
    #                  % (result.get('total_return_rate'),
    #                     result.get('max_drawdown'),
    #                     result.get('max_drawdown_period')))

    for stock in stock_pools:
        task = btasks.Task(bsm.MATrendStrategy, stock)
        result = task.task()
        logging.info('total return rate: %.2f, max drawdown: %.2f, max drawdown period: %.2f'
                     % (result.get('total_return_rate'),
                        result.get('max_drawdown'),
                        result.get('max_drawdown_period')))


if __name__ == '__main__':
    # download_delta_data()
    run_back_tesing()
