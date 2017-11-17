import datetime as dt
import json

import arctic

from backtradercn.libs.log import getLogger
from backtradercn.libs.wechat import WeChatClient
from backtradercn.settings import settings as conf
from backtradercn.libs.xueqiu_trader import XueQiuTrader


logger = getLogger(__name__)


def get_market_signal_by_date(date):
    msg = {
        'buy': [],
        'sell': [],
    }

    store = arctic.Arctic(conf.MONGO_HOST)
    lib_name = conf.DAILY_STOCK_ALERT_LIBNAME

    if lib_name not in store.list_libraries():
        logger.warning(f'can not find library: {lib_name} in Arctic')
    else:
        lib = store[lib_name]

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

    response = wx_client.send_all_text_message(
        json.dumps(msg, ensure_ascii=False))
    logger.debug(response)


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


if __name__ == '__main__':
    send_daily_alert()
    update_xueqiu_cubes()
