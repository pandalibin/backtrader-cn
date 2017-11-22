import datetime as dt
import json

from backtradercn.libs.log import get_logger
from backtradercn.libs.wechat import WeChatClient
from backtradercn.settings import settings as conf
from backtradercn.libs.xueqiu_trader import XueQiuTrader
from backtradercn.libs.models import get_library
from backtradercn.libs.sina import StockMatch
import time

logger = get_logger(__name__)


def get_market_signal_by_date(date):
    msg = {
        'buy': [],
        'sell': [],
    }

    lib = get_library(conf.DAILY_STOCK_ALERT_LIBNAME)
    if lib:
        if date in lib.list_symbols():
            data = lib.read(date).data
            data = data.to_dict('records')
            for item in data:
                if item['action'] == 'buy':
                    msg['buy'].append(item['stock'])
                elif item['action'] == 'sell':
                    msg['sell'].append(item['stock'])

    return msg


def send_daily_alert():
    date = dt.datetime.now().strftime('%Y-%m-%d')
    msg = get_market_signal_by_date(date)

    # send notification via wechat
    wx_client = WeChatClient({
        'APP_ID': conf.WECHAT_APP_ID,
        'APP_SECRET': conf.WECHAT_APP_SECRET,
    })

    try:
        response = wx_client.send_all_text_message(
            json.dumps(msg, ensure_ascii=False))
        logger.debug(response)
    except Exception as e:
        logger.error(e, exc_info=True)


def update_xueqiu_cubes():
    date = dt.datetime.now().strftime('%Y-%m-%d')
    msg = get_market_signal_by_date(date)
    trader = XueQiuTrader(
        xq_account=conf.XQ_ACCOUNT,
        xq_password=conf.XQ_PASSWORD,
        xq_portfolio_market=conf.XQ_PORTFOLIO_MARKET,
        xq_cube_prefix=conf.XQ_CUBES_PREFIX
    )

    for stock_code in msg['buy']:
        trader.buy(stock_code)

    for stock_code in msg['sell']:
        trader.sell(stock_code)


def update_sina_stock_match():
    date = dt.datetime.now().strftime('%Y-%m-%d')
    msg = get_market_signal_by_date(date)
    user = StockMatch(
        username=conf.SINA_CONFIG['username'],
        password=conf.SINA_CONFIG['password'],
    )
    for stock_code in msg['buy']:
        user.buy(stock_code)
        # 经过测试，每隔3S进行一次买入操作的频率最合适
        time.sleep(3)


if __name__ == '__main__':
    send_daily_alert()
    update_sina_stock_match()
