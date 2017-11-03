# -*- coding: utf-8 -*-
import backtradercn.tasks as btasks
import backtradercn.strategies.ma as bsm
from backtradercn.config.log import logging


logger = logging.getLogger(__name__)
stock_pools = ['000651']


def back_test():
    """
    Run back testing tasks via multiprocessing
    :return: None
    """
    for stock in stock_pools:
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


if __name__ == '__main__':
    back_test()
