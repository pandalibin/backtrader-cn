# -*- coding: utf-8 -*-


import backtrader as bt
import backtradercn.strategies.utils as bsu
import backtradercn.datas.tushare as bdt


class MATrendStrategy(bt.Strategy):
    """
    If short ma > long ma, then go to long market, else, go to short market.
    Attributes:
        sma_s(DataFrame): short term moving average.
        sma_l(DataFrame): long term moving average.
    """
    param = dict(
        ma_period_s=15,
        ma_perild_l=60
    )

    def __init__(self):
        super().__init__()

        self.sma_s = bt.indicators.MovingAverageSimple(
            self.datas[0], period=self.param.get('ma_period_s')
        )
        self.sma_l = bt.indicators.MovingAverageSimple(
            self.datas[0], period=self.param.get('ma_period_l')
        )

    def next(self):
        if not self.position:
            if self.sma_s > self.sma_l:
                bsu.Utils.order_target_percent(self, 1.0)

        else:
            if self.sma_s <= self.sma_l:
                bsu.Utils.order_target_percent(self, 0.0)

    @classmethod
    def get_data(cls, coll_name):
        """
        Get the time serials used by strategy.
        :param coll_name(string): stock id.
        :return: time serials(DataFrame).
        """
        ts_his_data = bdt.TsHisData(coll_name)

        return ts_his_data.get_data()
