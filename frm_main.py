# -*- coding: utf-8 -*-
import multiprocessing

import backtradercn.strategies.ma as bsm
import backtradercn.tasks as btasks
from backtradercn.libs.log import getLogger
from backtradercn.libs import models

logger = getLogger(__name__)


def back_test(stock):
    """
    Run back testing tasks via multiprocessing
    :return: None
    """

    task = btasks.Task(bsm.MATrendStrategy, stock)
    result = task.task()

    stock_id = result.get('stock_id')
    trading_days = result.get('trading_days')
    total_return_rate = result.get('total_return_rate')
    max_drawdown = result.get('max_drawdown')
    max_drawdown_period = result.get('max_drawdown_period')
    logger.debug(
        f'Stock {stock_id} back testing result, trading days: {trading_days:.2f}, '
        f'total return rate: {total_return_rate:.2f}, '
        f'max drawdown: {max_drawdown:.2f}, '
        f'max drawdown period: {max_drawdown_period:.2f}'
    )

    drawdown_points = result.get('drawdown_points')
    logger.debug('Draw down points:')
    for drawdown_point in drawdown_points:
        drawdown_point_dt = drawdown_point.get("datetime").isoformat()
        drawdown = drawdown_point.get('drawdown')
        drawdownlen = drawdown_point.get('drawdownlen')
        logger.debug(
            f'stock: {stock_id}, drawdown_point: {drawdown_point_dt}, '
            f'drawdown: {drawdown:.2f}, drawdownlen: {drawdownlen}'
        )


def main(stock_pools):
    """
    Get all stocks and run back test.
    :param stock_pools: list, the stock code list.
    :return: None
    """

    pool = multiprocessing.Pool()
    for stock in stock_pools:
        pool.apply_async(back_test, args=(stock, ))
    pool.close()
    pool.join()


if __name__ == '__main__':
    cn_stocks = models.get_cn_stocks()
    main(cn_stocks)
