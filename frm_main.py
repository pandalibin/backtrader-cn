# -*- coding: utf-8 -*-
import backtradercn.datas.tushare as bdt
import backtradercn.tasks as btasks
import backtradercn.strategies.ma as bsm
import logging

stock_pools = ['000651']

def back_test():
    """
    Run back testing tasks via multiprocessing
    :return: None
    """
    for stock in stock_pools:
        task = btasks.Task(bsm.MATrendStrategy, stock)
        result = task.task()
        logging.debug(
            'Stock %s back testing result, trading days: %.2f, total return rate: %.2f, max drawdown: %.2f, max drawdown period: %.2f'
            % (stock,
               result.get('trading_days'),
               result.get('total_return_rate'),
               result.get('max_drawdown'),
               result.get('max_drawdown_period')))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    back_test()
