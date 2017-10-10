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

    def __init__(self, db_addr, lib_name, *coll_names):
        self.db_addr = db_addr
        self.lib_name = lib_name
        self.coll_names = coll_names
        self.library = None
        self.unused_cols = ['price_change', 'p_change', 'ma5', 'ma10', 'ma20',
                            'v_ma5', 'v_ma10', 'v_ma20', 'turnover']

    def init_data(self):
        """
        Get all the history data when initiate the library.
        1. Connect to arctic and create the library.
        2. Get all the history data from tushare and strip the unused columns.
        3. Store the data to arctic.
        :return: None
        """
        store = arctic.Arctic(self.db_addr)
        store.delete_library(self.lib_name)
        store.initialize_library(self.lib_name)
        self.library = store[self.lib_name]

        for coll_name in self.coll_names:
            his_data = ts.get_hist_data(code=coll_name, retry_count=5).sort_index()
            if len(his_data) == 0:
                logging.warning('data of stock %s from tushare when initiation is empty' % coll_name)
                continue

            his_data = btu.Utils.strip_unused_cols(his_data, *self.unused_cols)

            self.library.write(coll_name, his_data)

    def download_delta_data(self):
        """
        Get yesterday's data and append it to collection.
        1. Connect to arctic and get the library.
        2. Get today's history data from tushare and strip the unused columns.
        3. Store the data to arctic.
        :return: None
        """
        store = arctic.Arctic(self.db_addr)
        self.library = store[self.lib_name]
        # This function is planed to be executed at each day's 8:30am,
        # so should get last day's data as delta
        end = dt.datetime.now() - dt.timedelta(days=1)
        start = end
        for coll_name in self.coll_names:
            his_data = ts.get_hist_data(code=coll_name, start=dt.datetime.strftime(start, '%Y-%m-%d'),
                                        end=dt.datetime.strftime(end, '%Y-%m-%d'), retry_count=5)
            if len(his_data) == 0:
                logging.warning('delta data of stock %s from tushare is empty' % coll_name)
                continue

            his_data = btu.Utils.strip_unused_cols(his_data, *self.unused_cols)

            self.library.append(coll_name, his_data)

    def get_data(self, coll_name):
        """
        Get all the data of one collection.
        :param coll_name(string): the name of collection.
        :return: data(DataFrame)
        """
        store = arctic.Arctic(self.db_addr)
        self.library = store[self.lib_name]

        return self.library.read(coll_name).data
