# -*- coding: utf-8 -*-
import easytrader
from easytrader import log
from backtradercn.settings import settings as conf
from backtradercn.libs.xq_client import XueQiuClient
from easytrader.exceptions import TradeError


class XueQiuTrader(object):
    """
    雪球组合操作类，适用于每个组合只能包含一直股票的买入和卖出操作
    """

    def __init__(self, xq_account, xq_password, xq_portfolio_market, xq_cube_prefix):
        self.xq_account = xq_account
        self.xq_password = xq_password
        self.xq_portfolio_market = xq_portfolio_market
        self.cube_prefix = xq_cube_prefix

    @property
    def client(self):
        """获取操作雪球组合的客户端
        :return:
        """
        if not hasattr(self, '_client'):
            self._client = XueQiuClient()
            self._client.prepare(
                account=self.xq_account,
                password=self.xq_password,
                portfolio_market=self.xq_portfolio_market
            )
        return self._client

    def get_current_weight(self, symbol):
        """获取组合股票当前百分比
        :param symbol: 组合编码
        :return:
        """
        portfolio_info = self.client.get_portfolio_info(symbol)
        position = portfolio_info['view_rebalancing']  # 仓位结构
        stocks = position['holdings']  # 持仓股票
        # 当前股票持仓为0%
        if len(stocks) == 0:
            return 0
        if len(stocks) > 1:
            raise TradeError("当前组合%s包含%d支股票，不适合当前的策略" % (symbol, len(stocks)))
        return stocks[0]['weight']

    def adjust_weight(self, symbol, stock_code, weight):
        """调整组合中股票的百分比
        :param symbol: 组合编码
        :param stock_code: 股票编码
        :param weight: 股票百分比
        :return:
        """
        if not hasattr(self, '_user'):
            self._user = easytrader.use('xq')
            self._user.prepare(
                account=self.xq_account,
                password=self.xq_password,
                portfolio_market=self.xq_portfolio_market,
                portfolio_code=symbol
            )
        self._user.adjust_weight(stock_code, weight)

    def buy(self, stock_code, weight=conf.XQ_DEFAULT_BUY_WEIGHT):
        """买入股票，默认一次买入指定的百分比数
        :param stock_code: 股票编码
        :param weight: 股票百分比
        :return:
        """
        symbol = self.is_cube_exist(stock_code)
        if symbol:
            current_weight = self.get_current_weight(symbol)
            if current_weight == 100:
                log.info("已经满仓，无法再买入股票%s" % stock_code)
                return
            new_weight = current_weight + weight
            if new_weight > 100:
                log.info("买入后, 股票%s的百分数超出100, 按照100买入" % stock_code)
                new_weight = 100
            self.adjust_weight(symbol, stock_code, new_weight)
            log.info("组合%s, 股票%s持仓由%s调整到%s" % (symbol, stock_code, current_weight, new_weight))
        else:
            created_success, symbol, cube_name = self.client.create_cube(stock_code, weight,
                                                                         cube_prefix=self.cube_prefix)
            if created_success:
                log.info("建仓成功。股票: %s, 组合名字: %s。组合代码: %s。" % (stock_code, cube_name, symbol))
            else:
                log.info("建仓失败。股票: %s" % stock_code)

    def is_cube_exist(self, stock_code):
        """检查满足组合前缀和股票代码的组合是否存在
        :param stock_code: 股票编码
         """
        cube_name = XueQiuClient.get_cube_name(self.cube_prefix, stock_code)
        cubes_list = self.client.get_cubes_list()
        for symbol, detail in cubes_list.items():
            if detail['name'] == cube_name:
                return symbol

    def sell(self, stock_code):
        """清仓
        :param stock_code: 股票编码
        """
        symbol = self.is_cube_exist(stock_code)
        if not symbol:
            log.info("当前没有包含股票%s的组合, 不需要卖出" % stock_code)
            return
        current_weight = self.get_current_weight(symbol)
        if current_weight == 0:
            log.info("组合%s, 股票%s已经处于空仓状态，不需要卖出" % (symbol, stock_code))
            return
        self.adjust_weight(symbol, stock_code, 0)
        log.info("组合%s, 股票%s清仓" % (symbol, stock_code))


if __name__ == '__main__':
    trader = XueQiuTrader(
        xq_account=conf.XQ_ACCOUNT,
        xq_password=conf.XQ_PASSWORD,
        xq_portfolio_market=conf.XQ_PORTFOLIO_MARKET,
        xq_cube_prefix=conf.XQ_CUBES_PREFIX,
    )
    trader.buy('601088')
    trader.sell('601088')
