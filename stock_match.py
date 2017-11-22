# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from backtradercn.settings import settings as conf
from backtradercn.libs.sina import StockMatch
from daily_alert import get_market_signal_by_date
from backtradercn.libs.log import get_logger

logger = get_logger(__name__)


def update_sina_stock_match():
    date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    msg = get_market_signal_by_date(date)
    user = StockMatch(
        username=conf.SINA_CONFIG['username'],
        password=conf.SINA_CONFIG['password'],
    )
    for stock_code in msg['buy']:
        user.buy(stock_code)
        # 经过测试，每隔3S进行一次买入操作的频率最合适
        time.sleep(3)
    else:
        logger.info("没有股票需要买入")


if __name__ == '__main__':
    update_sina_stock_match()
