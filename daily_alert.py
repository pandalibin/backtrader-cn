import datetime as dt
import arctic
import json

from backtradercn.settings import settings as conf
from backtradercn.libs.log import logging
from backtradercn.wechat.robot import WeChatClient


logger = logging.getLogger(__name__)


def send_daily_alert():
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

        symbol = dt.datetime.now().strftime('%Y-%m-%d')
        df = lib.read(symbol).data
        data = df.to_dict('records')
        for item in data:
            if item['action'] == 'buy':
                msg['buy'].append(item['stock'])
            elif item['action'] == 'sell':
                msg['sell'].append(item['stock'])

    # send notification via wechat
    wx_client = WeChatClient({
        'APP_ID': conf.WECHAT_APP_ID,
        'APP_SECRET': conf.WECHAT_APP_SECRET,
    })

    response = wx_client.send_all_text_message(
        json.dumps(msg, ensure_ascii=False))
    logger.debug(response)


if __name__ == '__main__':
    send_daily_alert()
