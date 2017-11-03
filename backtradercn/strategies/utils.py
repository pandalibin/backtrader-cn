# -*- coding: utf-8 -*-
from backtradercn.config.log import logging
import math
import pandas as pd


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

