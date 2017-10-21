# -*- coding: utf-8 -*-
import unittest
import backtradercn.datas.utils as bdu
import pandas as pd
import datetime as dt


class UtilsTestCase(unittest.TestCase):
    def test_run(self):
        self._test_strip_unused_cols()
        self._test_parse_data()

    def _test_parse_data(self):
        date_string = '2017-01-01'
        parsed_date = bdu.Utils.parse_date(date_string)

        self.assertEqual(parsed_date, dt.datetime(2017, 1, 1))

    def _test_strip_unused_cols(self):
        data = pd.DataFrame({
            'name': ['tom', 'jack'],
            'age': [24, 56],
            'gender': ['male', 'male'],
            'address': ['cn', 'us']
        })
        data.index = pd.date_range(start='2017-01-01', periods=2)

        origin_cols = ['name', 'age', 'gender', 'address']
        unused_cols = ['address', 'gender']
        new_cols = ['name', 'age']

        self.assertEqual(list(data.columns).sort(), origin_cols.sort())

        bdu.Utils.strip_unused_cols(data, *unused_cols)

        self.assertEqual(list(data.columns).sort(), new_cols.sort())
