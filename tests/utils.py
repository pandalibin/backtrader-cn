# -*- coding: utf-8 -*-
import backtrader as bt
import unittest


class Utils(unittest.TestCase):
    _DATA_PATH = './datas/2006-day-001'
    _DATA = bt.feeds.BacktraderCSVData(_DATA_PATH)

    def run_strategy_test(self, strategy, expected_value, expected_cash):
        """
        Test the strategy, the final portofolio vlaue should equal to the expected_value.
        :param strategy(Strategy): strategy to be tested.
        :param expected_value(float): expected portofolio value after the strategy is done.
        :param expected_cash(float): expected cash after the strategy is done.
        :param analyzer:
        :return: None
        """

        cerebro = bt.Cerebro()
        cerebro.adddata(self._DATA)
        cerebro.addstrategy(strategy)

        cerebro.run()

        value = cerebro.broker.get_value()
        cash = cerebro.broker.get_cash()

        self.assertEqual(value, expected_value)
        self.assertEqual(cash, expected_cash)
