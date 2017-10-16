# -*- coding: utf-8 -*-
import logging


class Utils(object):
    @classmethod
    def split_data(cls, data, percent=0.3):
        """
        Split the data into training data and test data.
        :param data(DataFrame): data to be split.
        :param percent(float): percent of data used as training data.
        :return: training data(DataFrame) and test data(DataFrame)
        """
        pass

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
