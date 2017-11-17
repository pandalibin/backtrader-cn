# -*- coding: utf-8 -*-
import multiprocessing
from multiprocessing import Process

import tushare as ts

import backtradercn.strategies.ma as bsm
import backtradercn.tasks as btasks
from backtradercn.libs.log import getLogger
from backtradercn.settings import settings as conf
from backtradercn.libs.models import drop_library, create_library


logger = getLogger(__name__)


def train(stock):
    """
    Run back testing tasks via multiprocessing
    :return: None
    """

    task = btasks.Task(bsm.MATrendStrategy, stock)
    task.train()


def main():
    hs300s = ts.get_hs300s()
    stock_pools = hs300s['code'].tolist() if 'code' in hs300s else []
    processes = multiprocessing.cpu_count()
    # run subprocess in parallel, the number of processes is: `processes`
    for i in range(len(stock_pools) // processes + 1):
        chunk_start = i * processes
        chunk_end = (i + 1) * processes
        chunk_lst = stock_pools[chunk_start:chunk_end]
        logger.debug(f'back test the chunk list: {chunk_lst}')
        procs = []
        for stock in chunk_lst:
            proc = Process(target=train, args=(stock,))
            procs.append(proc)
            proc.start()
        for proc in procs:
            proc.join()


if __name__ == '__main__':
    # drop params library, then re-create it with new data
    drop_library(conf.STRATEGY_PARAMS_LIBNAME)
    # create empty params library
    create_library(conf.STRATEGY_PARAMS_LIBNAME)

    # train('000651')
    main()

    # training 时会写数据到 `conf.DAILY_STOCK_ALERT_LIBNAME`
    drop_library(conf.DAILY_STOCK_ALERT_LIBNAME)
