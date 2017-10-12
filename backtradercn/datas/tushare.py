# -*- coding: utf-8 -*-
import arctic
import tushare as ts
import datetime as dt
import backtradercn.datas.utils as btu
import logging


class TsHisData(object):
    """
    Download and maintain history data from tushare, and provide other modules with the data.

    Attributes:
        db_addr(string): address of the mongodb.
        lib_name(string): name of library.
        coll_names(array): names(stock ids like '000651' for gree) of collections.

    """

    def __init__(self, db_addr, lib_name='ts_hist_lib', *coll_names):
        self._db_addr = db_addr
        self._lib_name = lib_name
        self._coll_names = coll_names
        self._library = None
        self._unused_cols = ['price_change', 'p_change', 'ma5', 'ma10', 'ma20',
                             'v_ma5', 'v_ma10', 'v_ma20', 'turnover']
        self._new_added_colls = []

    def download_delta_data(self):
        """
        Get yesterday's data and append it to collection,
        this method is planned to be excuted at each day's 8:30am to update the data.
        1. Connect to arctic and get the library.
        2. Get today's history data from tushare and strip the unused columns.
        3. Store the data to arctic.
        :return: None
        """
        store = arctic.Arctic(self._db_addr)

        # if library is not initialized
        if self._lib_name not in store.list_libraries():
            self._library = store.initialize_library(self._lib_name)

        self._library = store[self._lib_name]

        self._init_coll()

        # get last day's data as delta
        end = dt.datetime.now() - dt.timedelta(days=1)
        start = end
        for coll_name in self._coll_names:
            if coll_name in self._new_added_colls:
                continue
            his_data = ts.get_hist_data(code=coll_name, start=dt.datetime.strftime(start, '%Y-%m-%d'),
                                        end=dt.datetime.strftime(end, '%Y-%m-%d'), retry_count=5)
            if len(his_data) == 0:
                logging.warning('delta data of stock %s from tushare is empty' % coll_name)
                continue

            his_data = btu.Utils.strip_unused_cols(his_data, *self._unused_cols)

            self._library.append(coll_name, his_data)

    def get_data(self, coll_name):
        """
        Get all the data of one collection.
        :param coll_name(string): the name of collection.
        :return: data(DataFrame)
        """
        store = arctic.Arctic(self._db_addr)
        self._library = store[self._lib_name]

        return self._library.read(coll_name).data

    def _init_coll(self):
        """
        Get all the history data when initiate the library.
        1. Connect to arctic and create the library.
        2. Get all the history data from tushare and strip the unused columns.
        3. Store the data to arctic.
        :return: None
        """

        a = self

        for coll_name in self._coll_names:
            # if collection is not initialized
            if coll_name not in self._library.list_symbols():
                self._new_added_colls.append(coll_name)
                his_data = ts.get_hist_data(code=coll_name, retry_count=5).sort_index()
                if len(his_data) == 0:
                    logging.warning('data of stock %s from tushare when initiation is empty' % coll_name)
                    continue

                his_data = btu.Utils.strip_unused_cols(his_data, *self._unused_cols)

                self._library.write(coll_name, his_data)
