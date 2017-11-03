# -*- coding: utf-8 -*-
import tushare as ts
import multiprocessing
from multiprocessing import Process
import backtradercn.tasks as btasks
import backtradercn.strategies.ma as bsm
from backtradercn.config.log import logging


logger = logging.getLogger(__name__)


def back_test(stock):
    """
    Run back testing tasks via multiprocessing
    :return: None
    """

    task = btasks.Task(bsm.MATrendStrategy, stock)
    result = task.task()

    logger.debug(
        'Stock %s back testing result, trading days: %.2f, total return rate: %.2f, max drawdown: %.2f, max drawdown period: %.2f'
        % (stock,
            result.get('trading_days'),
            result.get('total_return_rate'),
            result.get('max_drawdown'),
            result.get('max_drawdown_period')))

    drawdown_points = result.get('drawdown_points')
    logger.debug('Draw down points:')
    for drawdown_point in drawdown_points:
        logger.debug(
            'stock: %s, drawdown_point: %s, drawdown: %.2f, drawdownlen: %d' % (
                stock,
                drawdown_point.get('datetime').isoformat(),
                drawdown_point.get('drawdown'),
                drawdown_point.get('drawdownlen')
            )
        )


def main():
    top_hs300 = ts.get_hs300s()
    stock_pools = ts.get_hs300s()['code'].tolist() if 'code' in top_hs300 else []
    processes = multiprocessing.cpu_count()
    length = len(stock_pools)
    multiprocessing.freeze_support()
    # 根据CPU数，一次处理 `processes` 支股票
    for i in range(int(length / processes) + 1):
        start = i * processes
        end = (i + 1) * processes
        lst = stock_pools[start:end]
        procs = []
        for stock in lst:
            proc = Process(target=back_test, args=(stock,))
            procs.append(proc)
            proc.start()
        for proc in procs:
            proc.join()


if __name__ == '__main__':
    # back_test('000651')
    main()
