# -*- coding: utf-8 -*-
import backtradercn.datas.tushare as bdt
import backtradercn.strategies.ma as bsm


class Task(object):
    """
    Task for each stock's back testing.
    Attributes:
        Strategy(Strategy): class of strategy used for back testing.
        stock_id(string): id of stock to be back tested.
    """

    def __init__(self, Strategy, stock_id):
        self._Strategy = Strategy
        self._stock_id = stock_id

    def task(self):
        """
        Task for each stock's back testing.
        1. Get the data.
        2. Split the data into training data and testing data.
        3. Find the optimized parameter of the strategy by using training data.
        4. Execute the back testing.
        5. Get the analysis data of the back testing(average annual return rate,
           max draw down, draw down length, average annual draw down).
        :return: analysis of this back testing(dict).
        """
        # Get the data
        data = bsm.MATrendStrategy.get_data(self._stock_id)

        # Split the data


