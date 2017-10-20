# -*- coding: utf-8 -*-
import backtradercn.strategies.ma as bsm
import backtradercn.strategies.utils as bsu


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
        data = self._Strategy.get_data(self._stock_id)

        # Split the data
        training_data, testing_data = bsu.Utils.split_data(data)

        # Find the optimized parameter by using training data
        best_param = self._Strategy.train_strategy(training_data)

        # Run back testing, get the analysis data
        result = self._Strategy.run_back_testing(testing_data, best_param)

        return result
