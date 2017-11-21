# -*- coding: utf-8 -*-


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
        1. Execute the back testing.
        2. Get the analysis data of the back testing(average annual return rate,
           max draw down, draw down length, average annual draw down).
        :return: analysis of this back testing(dict).
        """
        # Get the data
        # data = self._Strategy.get_data(self._stock_id)

        # Split the data
        # training_data, testing_data = bsu.Utils.split_data(data)

        # Find the optimized parameter by using training data
        # best_param = self._Strategy.train_strategy(training_data, self._stock_id)

        # best_param = dict(
        #     ma_periods=dict(
        #         ma_period_s=10,
        #         ma_period_l=20,
        #         stock_id=self._stock_id
        #
        #     )
        # )

        # Run back testing, get the analysis data
        # result = self._Strategy.run_back_testing(data, best_param)

        result = self._Strategy.run_back_testing(self._stock_id)

        return result

    def train(self):
        return self._Strategy.run_training(self._stock_id)
