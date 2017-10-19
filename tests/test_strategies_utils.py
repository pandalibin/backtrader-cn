# -*- coding: utf-8 -*-
import unittest
import backtradercn.strategies.utils as bsu
import datetime as dt
import pandas as pd
import numpy as np


class UtilsTestCase(unittest.TestCase):
    def test_run(self):
        self._test_parse_data()
        self._test_split_data()
        self._test_get_best_params()

    def _test_parse_data(self):
        date_string = '2017-01-01'
        parsed_date = bsu.Utils.parse_date(date_string)

        self.assertEqual(parsed_date, dt.datetime(2017, 1, 1))

    def _test_split_data(self):
        data = pd.DataFrame(np.random.rand(10, 2))
        data.index = ['2017-01-01', '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05',
                      '2017-01-06', '2017-01-07', '2017-01-08', '2017-01-09', '2017-01-10']

        training_data, testing_data = bsu.Utils.split_data(data, 0.3)
        training_data_len = len(training_data)

        training_data_last = training_data[1][-1]
        training_data_target = data[1][training_data_len - 1]
        testing_data_first = testing_data[0][0]
        testing_data_target = data[0][training_data_len]
        self.assertEqual(training_data_last, training_data_target)
        self.assertEqual(testing_data_first, testing_data_target)

    def _test_get_best_params(self):
        al_results = []

        for i in range(10):
            al_result = dict(
                params=None,
                total_return_rate=np.random.randint(1, 10),
                max_drawdown=0,
                max_drawdown_period=0
            )
            al_results.append(al_result)

        best_al_result = bsu.Utils.get_best_params(al_results)

        best_return_rate = best_al_result.get('total_return_rate')
        for i in range(10):
            self.assertGreaterEqual(best_return_rate, al_results[i].get('total_return_rate'))
