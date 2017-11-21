# -*- coding: utf-8 -*-
import multiprocessing
from multiprocessing import Process, Lock

import backtradercn.strategies.ma as bsm
import backtradercn.tasks as btasks
from backtradercn.libs.log import getLogger
from backtradercn.settings import settings as conf
from backtradercn.libs import models


logger = getLogger(__name__)


def train(stock, lock):
    """
    Run training tasks via multiprocessing and save training params to arctic store.
    :param stock: str, stock code
    :param lock: the instance of multiprocessing.Lock
    :return: None
    """

    task = btasks.Task(bsm.MATrendStrategy, stock)
    params = task.train()
    # write stock params to MongoDB
    symbol = conf.STRATEGY_PARAMS_MA_SYMBOL
    with lock:
        models.save_training_params(symbol, params)


def main():
    """
    Get all stocks and train params for each stock.
    :return: None
    """

    stock_pools = models.get_cn_stocks()
    lock = Lock()
    processes = multiprocessing.cpu_count()
    # run subprocess in parallel, the number of processes is: `processes`
    for i in range(len(stock_pools) // processes + 1):
        chunk_start = i * processes
        chunk_end = (i + 1) * processes
        chunk_lst = stock_pools[chunk_start:chunk_end]
        if not chunk_lst:
            break

        logger.debug(f'back test the chunk list: {chunk_lst}')
        procs = []
        for stock in chunk_lst:
            proc = Process(target=train, args=(stock, lock))
            procs.append(proc)
            proc.start()
        for proc in procs:
            proc.join()


if __name__ == '__main__':
    # drop params library, then re-create it with new data
    models.drop_library(conf.STRATEGY_PARAMS_LIBNAME)
    # create empty params library
    models.create_library(conf.STRATEGY_PARAMS_LIBNAME)

    # train('000651')
    # train('000001')

    main()

    # training 时会写数据到 `conf.DAILY_STOCK_ALERT_LIBNAME`
    models.drop_library(conf.DAILY_STOCK_ALERT_LIBNAME)
