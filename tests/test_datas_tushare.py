import unittest
import backtradercn.datas.tushare as bdt
from backtradercn.settings import settings as conf
import unittest.mock as um
import pandas as pd
import datetime as dt
import arctic


class TsHisDataTestCase(unittest.TestCase):
    def test_run(self):
        self._test_download_delta_data_initial_no_data()
        self._test_download_delta_data_initial()
        self._test_download_delta_data_no_data()
        self._test_download_delta_data()

    @um.patch('tushare.get_hist_data')
    def _test_download_delta_data_initial_no_data(self, mock_get_hist_data):
        mock_hist_data = pd.DataFrame()

        mock_get_hist_data.return_value = mock_hist_data

        coll_name = '000651'
        ts_his_data = bdt.TsHisData(coll_name)

        store = arctic.Arctic('localhost')
        store.delete_library(conf.CN_STOCK_LIBNAME)

        ts_his_data.download_delta_data()

        self.assertEqual(len(ts_his_data._library.list_symbols()), 0)

    @um.patch('tushare.get_hist_data')
    def _test_download_delta_data_initial(self, mock_get_hist_data):
        mock_hist_data = pd.DataFrame(data={
            'open': [10, 11],
            'high': [12, 13],
            'close': [14, 15],
            'low': [16, 17],
            'volume': [18, 19],
            'price_change': [20, 21],
            'p_change': [22, 23],
            'ma5': [24, 25],
            'ma10': [26, 27],
            'ma20': [28, 29],
            'v_ma5': [30, 31],
            'v_ma10': [32, 33],
            'v_ma20': [34, 35],
            'turnover': [36, 37]
        }, index=['2017-01-01', '2017-01-02'])

        mock_get_hist_data.return_value = mock_hist_data

        coll_name = '000651'
        ts_his_data = bdt.TsHisData(coll_name)

        store = arctic.Arctic('localhost')
        store.delete_library(conf.CN_STOCK_LIBNAME)

        ts_his_data.download_delta_data()

        hist_data_000651 = ts_his_data.get_data()

        self.assertEqual(len(hist_data_000651), 2)

    @um.patch('tushare.get_hist_data')
    def _test_download_delta_data_no_data(self, mock_get_hist_data):
        coll_name = '000651'
        ts_his_data = bdt.TsHisData(coll_name)

        mock_delta_data = pd.DataFrame()
        mock_get_hist_data.return_value = mock_delta_data

        ts_his_data.download_delta_data()

        hist_data_000651 = ts_his_data.get_data()

        self.assertEqual(len(hist_data_000651), 2)

    @um.patch('tushare.get_hist_data')
    def _test_download_delta_data(self, mock_get_hist_data):
        coll_name = '000651'
        ts_his_data = bdt.TsHisData(coll_name)

        yesterday = dt.datetime.now() - dt.timedelta(days=1)
        mock_delta_data = pd.DataFrame(data={
            'open': 38,
            'high': 39,
            'close': 40,
            'low': 41,
            'volume': 42,
            'price_change': 43,
            'p_change': 44,
            'ma5': 45,
            'ma10': 46,
            'ma20': 47,
            'v_ma5': 48,
            'v_ma10': 49,
            'v_ma20': 50,
            'turnover': 51
        }, index=[dt.datetime.strftime(yesterday, '%Y-%m-%d')])

        mock_get_hist_data.return_value = mock_delta_data

        ts_his_data.download_delta_data()

        hist_data_000651 = ts_his_data.get_data()

        self.assertEqual(len(hist_data_000651), 3)
        self.assertEqual(dt.datetime.strftime(hist_data_000651.index[-1], '%Y-%m-%d'),
                         dt.datetime.strftime(yesterday, '%Y-%m-%d'))
