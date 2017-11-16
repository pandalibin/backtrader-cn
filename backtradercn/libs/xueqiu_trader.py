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

    def __init__(self, xq_account, xq_password, xq_portfolio_market, xq_cube_prefix, stock_code):
        self.xq_account = xq_account
        self.xq_password = xq_password
        self.xq_portfolio_market = xq_portfolio_market
        self.stock_code = stock_code
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

    def adjust_weight(self, symbol, weight):
        """调整组合中股票的百分比
        :param symbol: 组合编码
        :param weight: 股票百分比
        :return:
        """
        user = easytrader.use('xq')
        user.prepare(
            account=self.xq_account,
            password=self.xq_password,
            portfolio_market=self.xq_portfolio_market,
            portfolio_code=symbol
        )

        user.adjust_weight(self.stock_code, weight)

    def buy(self, weight=conf.XQ_DEFAULT_BUY_WEIGHT):
        """买入股票，默认一次买入指定的百分比数
        :return:
        """
        symbol = self.is_cube_exist()
        if symbol:
            current_weight = self.get_current_weight(symbol)
            self.adjust_weight(symbol, current_weight + weight)
            log.info("组合%s, 股票%s持仓由%s调整到%s" % (symbol, self.stock_code, current_weight, current_weight + weight))
        else:
            created_success, symbol, cube_name = self.client.create_cube(self.stock_code, weight,
                                                                         cube_prefix=self.cube_prefix)
            if created_success:
                log.info("建仓成功。股票: %s, 组合名字: %s。租合代码: %s。" % (self.stock_code, cube_name, symbol))
            else:
                log.info("建仓失败。股票: %s" % self.stock_code)

    def is_cube_exist(self):
        """检查满足组合前缀和股票代码的组合是否存在 """
        cube_name = XueQiuClient.get_cube_name(self.cube_prefix, self.stock_code)
        cubes_list = self.client.get_cubes_list()
        for symbol, detail in cubes_list.items():
            if detail['name'] == cube_name:
                return symbol

    def sell(self):
        """清仓"""
        symbol = self.is_cube_exist()
        if not symbol:
            log.info("当前没有包含股票%s的组合, 不需要卖出" % self.stock_code)
            return
        current_weight = self.get_current_weight(symbol)
        if current_weight == 0:
            log.info("组合%s, 股票%s已经处于空仓状态，不需要卖出" % (symbol, self.stock_code))
            return
        self.adjust_weight(symbol, 0)
        log.info("组合%s, 股票%s清仓" % (symbol, self.stock_code))


if __name__ == '__main__':
    trader = XueQiuTrader(xq_account=conf.XQ_ACCOUNT,
                          xq_password=conf.XQ_PASSWORD,
                          xq_portfolio_market=conf.XQ_PORTFOLIO_MARKET,
                          xq_cube_prefix=conf.XQ_CUBES_PREFIX,
                          stock_code='000651')
    trader.buy()
    trader.sell()
