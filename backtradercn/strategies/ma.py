# -*- coding: utf-8 -*-


import backtrader as bt
import backtradercn.strategies.utils as bsu
import backtradercn.datas.tushare as bdt
import math


class MATrendStrategy(bt.Strategy):
    """
    If short ma > long ma, then go to long market, else, go to short market.
    Attributes:
        sma_s(DataFrame): short term moving average.
        sma_l(DataFrame): long term moving average.
    """

    # TODO(pandalibin):try tuple as params ==================>

    params = dict(
        ma_periods=dict(
            ma_period_s=15,
            ma_period_l=60
        )
    )

    def __init__(self):
        super().__init__()

        self.sma_s = bt.indicators.MovingAverageSimple(
            self.datas[0], period=self.params.ma_periods.get('ma_period_s')
        )
        self.sma_l = bt.indicators.MovingAverageSimple(
            self.datas[0], period=self.params.ma_periods.get('ma_period_l')
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

    @classmethod
    def get_params_list(cls, training_data):
        """
        Get the params list for finding the best strategy.
        :param training_data: data for training.
        :return: list(dict)
        """
        params_list = []
        data_len = len(training_data)

        #ma_s_len = math.floor(data_len * 0.3)
        ma_s_len = 2

        for i in range(1, ma_s_len):
            for j in range(i, data_len, 5):
                params = dict(
                    ma_period_s=i,
                    ma_period_l=j
                )
                params_list.append(params)

        return params_list

    @classmethod
    def train_strategy(cls, training_data):
        """
        Find the optimized parameter of the stategy by using training data.
        :param training_data(DataFrame): data used to train the strategy.
        :return: params(dict)
        """
        # get the params list
        params_list = cls.get_params_list(training_data)

        al_results = []

        cerebro = bt.Cerebro()
        data = bt.feeds.PandasData(dataname=training_data)

        cerebro.adddata(data)
        cerebro.optstrategy(cls, ma_periods=params_list)
        cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='al_return',
                            timeframe=bt.analyzers.TimeFrame.NoTimeFrame)
        cerebro.addanalyzer(bt.analyzers.TimeDrawDown, _name='al_max_drawdown')

        cerebro.broker.set_cash(bsu.Utils.DEFAULT_CASH)
        cerebro.broker.setcommission(bsu.Utils.DEFAULT_COMM)

        results = cerebro.run()

        for result in results:
            params = result[0].params
            analyzers = result[0].analyzers
            al_return_rate = analyzers.al_return.get_analysis()
            total_return_rate = 0.0
            for k, v in al_return_rate.items():
                total_return_rate = v
            al_result = dict(
                params=params,
                total_return_rate=total_return_rate,
                max_drawdown=analyzers.al_max_drawdown.get_analysis().get('maxdrawdown'),
                max_drawdown_period=analyzers.al_max_drawdown.get_analysis().get('maxdrawdownperiod')
            )
            al_results.append(al_result)

        # Get the best params
        best_al_result = bsu.Utils.get_best_params(al_results)

        return best_al_result.get('params')

    @classmethod
    def run_back_testing(cls, testing_data, **params):
        """
        Run the back testing, return the analysis data.
        :param testing_data(DataFrame): data for back testing.
        :param param(dict): params of strategy.
        :return(dict): analysis data.
        """
        cerebro = bt.Cerebro()
        data = bt.feeds.PandasData(dataname=testing_data)

        cerebro.adddata(data)
        cerebro.addstrategy(cls, ma_periods=dict(ma_period_s=params.get('ma_period_s'),
                            ma_period_l=params.get('ma_period_l')))
        cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='al_return',
                            timeframe=bt.analyzers.TimeFrame.NoTimeFrame)
        cerebro.addanalyzer(bt.analyzers.TimeDrawDown, _name='al_max_drawdown')

        cerebro.broker.set_cash(bsu.Utils.DEFAULT_CASH)
        cerebro.broker.setcommission(bsu.Utils.DEFAULT_COMM)

        strats = cerebro.run()
        strat = strats[0]

        for k, v in strat.analyzers.al_return.get_analysis().items():
            total_return_rate = v

        al_result = dict(
            total_return_rate=total_return_rate,
            max_drawdown=strat.analyzers.al_max_drawdown.get_analysis().get('maxdrawdown'),
            max_drawdown_period=strat.analyzers.al_max_drawdown.get_analysis().get('maxdrawdownperiod')
        )

        return al_result
