# -*- coding: utf-8 -*-
import math

import pandas as pd
import arctic

from backtradercn.settings import settings as conf
from backtradercn.libs.log import logging

logger = logging.getLogger(__name__)


class Utils(object):

    DEFAULT_CASH = 10000.0

    @classmethod
    def split_data(cls, data, percent=0.3):
        """
        Split the data into training data and test data.
        :param data(DataFrame): data to be split.
        :param percent(float): percent of data used as training data.
        :return: training data(DataFrame) and testing data(DataFrame)
        """

        rows = len(data)
        train_rows = math.floor(rows * percent)
        test_rows = rows - train_rows

        return data.iloc[:train_rows], data.iloc[-test_rows:]

    @classmethod
    def log(cls, dt, txt):
        """
        Logging function for strategy, level is info.
        :param dt(datetime): datetime for bar.
        :param txt(string): txt to be logged.
        :return: None
        """
        logger.debug('%s, %s' % (dt.isoformat(), txt))

    @classmethod
    def get_best_params(cls, al_results):
        """
        Get the best params, current algorithm is the largest total return rate.
        :param al_results(list): all the optional params and corresponding analysis data.
        :return: best params and corresponding analysis data(dict)
        """
        al_results_df = pd.DataFrame.from_dict(al_results)
        al_results_df = al_results_df.sort_values('total_return_rate', ascending=False)

        al_result_dict = al_results_df.iloc[0].to_dict()

        return al_result_dict

    @classmethod
    def write_daily_alert(cls, symbol, data):
        """
        write daily stock alert to MongoDB.
        :param symbol: Arctic symbol
        :param data: dict, like: {'stock': '000651', 'action': 'buy/sell'}
        :return: None
        """

        mongo_host = conf.MONGO_HOST
        lib_name = conf.DAILY_STOCK_ALERT_LIBNAME
        store = arctic.Arctic(mongo_host)
        if lib_name not in store.list_libraries():
            store.initialize_library(lib_name)
        lib = store[lib_name]

        df = pd.DataFrame([data], columns=data.keys())
        if symbol in lib.list_symbols():
            lib.append(symbol, df)
        else:
            lib.write(symbol, df)
