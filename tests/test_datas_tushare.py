import unittest
import backtradercn.datas.tushare as bdt
import unittest.mock as um
import tushare
import pandas as pd


class TsHisDataTestCase(unittest.TestCase):
    @um.patch('tushare.get_hist_data')
    def test_init_data(self, mock_get_hist_data):
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

        coll_names = ['000651', '600085']
        ts_his_data = bdt.TsHisData('localhost', 'ts_hist_lib', *coll_names)

        ts_his_data.init_data()

        hist_data_000651 = ts_his_data.get_data('000651')
        hist_data_600085 = ts_his_data.get_data('600085')

        self.assertEqual(len(hist_data_000651), 2)
        self.assertEqual(len(hist_data_600085), 2)

