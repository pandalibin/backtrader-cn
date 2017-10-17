# -*- coding: utf-8 -*-
import logging
import math
import pandas as pd
import datetime


class Utils(object):

    DEFAULT_CASH = 10000
    # 0.0625%
    DEFAULT_COMM = 0.0625

    @classmethod
    def parse_date(cls, date_string):
        return datetime.datetime.strptime(date_string, '%Y-%m-%d')

    @classmethod
    def split_data(cls, data, percent=0.3):
        """
        Split the data into training data and test data.
        :param data(DataFrame): data to be split.
        :param percent(float): percent of data used as training data.
        :return: training data(DataFrame) and testing data(DataFrame)
        """

        # parse the date
        data.index = data.index.map(cls.parse_date)

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
        logging.info('%s, %s' % (dt.isoformat(), txt))

    @classmethod
    def order_target_percent(cls, strategy, target=0.0):
        """
        Place an order to rebalance a postion to have final value of target percentage of
        current portfolio value and notify the user.
        :param strategy(Strategy): current strategy instance.
        :param target(float): target percentage of portfolio value.
        :return: None
        """
        strategy.order_target_percent(strategy.datas[0])
        cls.log(dt=strategy.datas[0].datetime.date(),
                txt='Adjust position percentage to %f.' % target)

        if strategy.datas[0].datetime.date() == datetime.datetime.now().date():
            logging.info('==>Notify customer to adjust the position.')



    @classmethod
    def get_best_params(cls, al_results):
        """
        Get the best params, current algorithm is the largest total return rate.
        :param al_results(list): all the optional params and corresponding analysis data.
        :return: best params and corresponding analysis data(dict)
        """
        al_results_df = pd.DataFrame.from_dict(al_results)
        al_results_df = al_results_df.sort_values('total_return_rate', ascending=False)

        return al_results_df.iloc[0].to_dict()

