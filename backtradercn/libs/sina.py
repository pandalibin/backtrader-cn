# -*- coding: utf-8 -*-
import base64
import json
import random
import re
import string
import time
import urllib.parse
from collections import namedtuple
from datetime import datetime
from enum import IntEnum
from pprint import pprint

import demjson
import requests
from retrying import retry

from backtradercn.libs.log import get_logger
from backtradercn.settings import settings as conf

logger = get_logger(__name__)


def enable_debug_requests():
    # Enabling debugging at http.client level (requests->urllib3->http.client)
    # you will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # the only thing missing will be the response.body which is not logged.
    from http.client import HTTPConnection
    import logging

    HTTPConnection.debuglevel = 1
    logger.setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


# 去掉注释，开启调试模式
# enable_debug_requests()

def pretty_print(data):
    print(json.dumps(data, indent=4, ensure_ascii=False))


def pretty_print_namedtuple(namedtuple_obj):
    pprint(dict(namedtuple_obj._asdict()))


def _json_object_hook(d):
    class_name = d.pop('_class_name', 'NamedTuple')
    return namedtuple(class_name, d.keys())(*d.values())


def json2obj(data):
    """将json转换为对象"""
    return json.loads(data, object_hook=_json_object_hook)


def get_unix_timestamp(with_millisecond=True):
    """
    get unix时间戳
    :param with_millisecond: 是否返回毫秒信息
    :return:
    """
    return int(time.time() * 1000) if with_millisecond else int(time.time())


def get_random_string(length=8, digits_only=True):
    """
    获取随机字符串长度
    :param length:
    :param digits_only:
    :return:
    """
    random_str = ""
    random_list = string.digits if digits_only else string.ascii_letters + string.digits
    for i in range(length):
        random_str += random.choice(random_list)
    return random_str


def extract_stock_info(stock_str):
    """解析股票信息
    :param stock_str:
    :return:
    >>> empty_stock_str="var suggestdata_1511245999245="";"
    >>> extract_stock_info(empty_stock_str)
    []
    >>> cn_stock_str='var suggestdata_1511246914696="格力电器,111,000651,sz000651,格力电器,gldq,格力电器,0;格力地产,111,600185,sh600185,格力地产,gldc,格力地产,0";'
    >>> extract_stock_info(cn_stock_str)
    [{'name': '格力电器', 'type': '111', 'stock_code': '000651', 'symbol': 'sz000651', 'first_letters': 'gldq'}, {'name': '格力地产', 'type': '111', 'stock_code': '600185', 'symbol': 'sh600185', 'first_letters': 'gldc'}]

    >>> us_stock_str='var suggestdata_1511246560937="阿里巴巴,41,baba,alibaba group,阿里巴巴,albb,阿里巴巴,10;阿里那,41,arna,arena pharmaceuticals,阿里那,aln,阿里那,0;阿里阿德,41,aria,ariad pharmaceuticals,阿里阿德,alad,阿里阿德,0";'
    >>> extract_stock_info(us_stock_str)
    [{'name': '阿里巴巴', 'type': '41', 'stock_code': 'baba', 'symbol': 'alibaba group', 'first_letters': 'albb'}, {'name': '阿里那', 'type': '41', 'stock_code': 'arna', 'symbol': 'arena pharmaceuticals', 'first_letters': 'aln'}, {'name': '阿里阿德', 'type': '41', 'stock_code': 'aria', 'symbol': 'ariad pharmaceuticals', 'first_letters': 'alad'}]
    """
    stocks = []
    match = re.search(r'"(.*)"', stock_str)
    if not match:
        return stocks
    stock_info = match.groups()[0]
    str_stocks = stock_info.split(";")
    for stock in str_stocks:
        search_key, market_type, stock_code, symbol, name, first_letters, _, _ = stock.split(
            ',')
        stocks.append(
            {
                "name": name,
                "type": market_type,
                "stock_code": stock_code,
                "symbol": symbol,
                "first_letters": first_letters,
            }
        )
    return stocks


def jsonp2dict(jsonp):
    """
    解析jsonp类型的返回
    :param jsonp:
    :return:
    """

    try:
        l_index = jsonp.index("(") + 2
        r_index = jsonp.rindex(")") - 1
        jsonp_info = jsonp[l_index:r_index]
    except ValueError:
        logger.error("Input is not in a jsonp format. %s" % jsonp)
        return
    try:
        return demjson.decode(jsonp_info)
    except demjson.JSONDecodeError as e:
        if jsonp_info == "new Boolean(true)":
            return True
        elif jsonp_info == "null":
            return None
        else:
            logger.error("解析jsonp返回失败")
            logger.error(jsonp)
            raise e


def check_error(res_dict):
    """
    检测返回值中是否包含错误的返回码。
    如果返回码提示有错误，抛出一个异常
    """
    if "retcode" in res_dict:
        if res_dict['retcode'] == 1005:
            logger.warning("下单失败, 操作过快，即将重试!")
            raise HighFrequencyError("{}: {}".format(res_dict["retcode"], res_dict["msg"]))
        raise StockMatchError("{}: {}".format(res_dict["retcode"], res_dict["msg"]))
    raise StockMatchError(json.dumps(res_dict))


def retry_if_if_high_frequency(exception):
    """Return True if we should retry (in this case when it's an IOError), False otherwise"""
    return isinstance(exception, HighFrequencyError)


class OrderStatus(IntEnum):
    # 未成交
    undealt = 0
    # 成交
    dealt = 1
    # 已经撤销
    canceled = 2

    def __str__(self):
        return '%s' % self.value


class StockMatchError(Exception):
    """异常处理"""

    def __init__(self, message=None):
        super(StockMatchError, self).__init__()
        self.message = message


class LoginFailedError(StockMatchError):
    """登录失败"""
    pass


class HighFrequencyError(StockMatchError):
    """操作频率太快"""
    pass


class StockMatch(object):
    """
    新浪模拟炒股
    沪深练习场

    http://jiaoyi.sina.com.cn/jy/index.php
    """

    def __init__(self, username, password):
        self.session, self.uid = self.login(username, password)

    # 注意: 目前采用的登录方式没有对密码做RSA加密
    # 参考
    # http://lovenight.github.io/2015/11/23/Python-%E6%A8%A1%E6%8B%9F%E7%99%BB%E5%BD%95%E6%96%B0%E6%B5%AA%E5%BE%AE%E5%8D%9A/
    # http://www.jianshu.com/p/816594c83c74
    def login(self, username, password):
        """
        # 新浪微博登录
        :param username: 微博手机号
        :param password: 微博密码
        :return:
        """
        if username == "" or password == "":
            raise StockMatchError("用户名或密码不能为空")
        post_data = {
            "entry": "finance",
            "gateway": "1",
            "from": None,
            "savestate": "30",
            "qrcode_flag": True,
            "useticket": "0",
            "pagerefer": "http://jiaoyi.sina.com.cn/jy/index.php",
            "vsnf": "1",
            "su": base64.b64encode(username.encode("utf-8")).decode("utf-8"),
            "service": "sso",
            "servertime": get_unix_timestamp(False),
            "nonce": "RA12UM",
            # "pwencode": "rsa2",  # 取消掉使用rsa2加密密码
            "sp": password,
            "sr": "1280*800",
            "encoding": "UTF-8",
            "cdult": "3",
            "domain": "sina.com.cn",
            "prelt": "56",
            "returntype": "TEXT",
        }
        session = requests.Session()
        session.headers.update(conf.SINA_CONFIG["request_headers"])
        res = session.post(conf.SINA_CONFIG["login_url"], data=post_data, params={
            "client": "ssologin.js(v1.4.19)",
            "_": get_unix_timestamp(),
        })
        res.encoding = "gb2312"
        info = json.loads(res.content)
        if info["retcode"] != "0":
            logger.error(info["reason"])
            raise LoginFailedError(info["reason"])
        logger.info("用户%s登录成功" % username)
        return session, info['uid']

    @property
    def available_fund(self):
        """获取当前可用资产"""
        return self.get_account_info()['AvailableFund']

    # 返回字段含义参考
    # http://n.sinaimg.cn/finance/jiaoyi/js/STP.js
    def get_account_info(self):
        """
        获取账户基本信息
        :return:
        {
            "sid": 1768615155,  # 用户ID
            "contest_id": 10000, # 比赛ID
            "match_id": "1",  # 比赛ID
            "StockFund": "500000.000", # 资产
            "AvailableFund": "500000.000", # 可用资金
            "WarrantFund": "0.000",
            "LastTotalFund": "500000.000",
            "ctime": "2017-11-20 11:32:03",
            "ProfitRatio": "0.000",
            "StockProfit": "0.000", # 当日盈亏
            "StockCode": "",
            "StockName": "",
            "max_profit_ratio": "",
            "rank": "--",   # 比赛排名
            "rank_yesterday": "",
            "rank_week": "",    # 周排行
            "rank_month": "",   # 月排行
            "profit_ratio": "--",  # 比赛收益
            "profit_ratio_day": "", # 当日收益
            "profit_ratio_week": "", # 周收益率
            "profit_ratio_month": "", #月收益率
            "success_ratio": "",
            "frequency": "",
            "industry": "",
            "stockhold": ""
        }
        """

        url = "http://jiaoyi.sina.com.cn/api/jsonp_v2.php/jsonp_%s_%s/Account_Service.getAccountinfo" % (
            get_unix_timestamp(), get_random_string())

        r = self.session.get(url, params={
            "sid": self.uid,
            "contest_id": 10000,
        })
        return jsonp2dict(r.text)

    def _query_orders(self, from_position=0, per_page=10):
        """
        查询当日委托
        :param from_position: 从第几个开始
        :param per_page: 每页返回个数
        :return:
        """
        url = "http://jiaoyi.sina.com.cn/api/jsonp_v2.php/jsonp_%s_%s/V2_CN_Order_Service.getOrder" % (
            get_unix_timestamp(), get_random_string())
        r = self.session.get(
            url, params={
                "sid": self.uid,
                "cid": 10000,
                "sdate": datetime.strftime(datetime.now(), '%Y-%m-%d'),
                "edate": "",
                "from": from_position,  # 请求偏移0
                "count": per_page,  # 每个返回个数
                "sort": 1
            })
        return jsonp2dict(r.text)

    # fixme:
    # 调用新浪接口发现返回的是所有委托，请求时的传递的时间参数没有任何作用
    def get_today_orders(self, status=None):
        """
        获取当日委托,
        :param status: 委托状态: "0": 未成交委托, "1": 成交的委托, "2":已撤销委托，默认返回当天所有委托
        :return:
        [Order(og_id='120350', contest_id='10000', sid='5175517774', StockCode='sz000651', StockName='格力电器', SellBuy='0', OrderPrice='47.800', DealAmount='100', OrderAmount='100', IfDealt='2', OrderTime='2017-11-21 17:30:10', mtime='2017-11-21 17:33:40')]

        {
            "data": [
                {
                    "og_id": "120350",  # 委托ID
                    "contest_id": "10000", # 比赛ID
                    "sid": "5175517774",
                    "StockCode": "sz000651",
                    "StockName": "格力电器",
                    "SellBuy": "0",   # 0表示买入
                    "OrderPrice": "47.800",
                    "DealAmount": "100",
                    "OrderAmount": "100",
                    "IfDealt": "2", # 成交状态: 0: 未成交，2: 已撤销
                    "OrderTime": "2017-11-21 17:30:10", # 委托创建时间
                    "mtime": "2017-11-21 17:33:40"
                },
        """
        if isinstance(status, int):
            status = str(status)
        from_position = 0
        per_page = 10
        obj_stocks = []
        while True:
            json_stocks = self._query_orders(from_position, per_page)
            for stock in json_stocks['data']:
                stock['_class_name'] = 'Order'
                if status is None:
                    obj_stocks.append(json2obj(json.dumps(stock)))
                elif stock['IfDealt'] == status:
                    obj_stocks.append(json2obj(json.dumps(stock)))
            if from_position + per_page >= int(json_stocks['count']):
                break
            from_position += per_page

        return obj_stocks

    def cancel_all_orders(self):
        """
        撤销所有未成交的委托
        :return:
        """
        orders = self.get_today_orders(OrderStatus.undealt)
        for order in orders:
            self.cancel_order(order)

    def cancel_order(self, order):
        """
        撤销委托
        :param order:
        :return:
        """
        url = "http://jiaoyi.sina.com.cn/api/jsonp_v2.php/jsonp_%s_%s/Order_Service.cancel" % (
            get_unix_timestamp(), get_random_string())
        r = self.session.get(url, params={
            "sid": self.uid,
            "cid": 10000,
            "order_id": order.og_id
        })
        res = jsonp2dict(r.text)
        if isinstance(res, bool) and res:
            logger.info("撤销委托成功。%s" % str(order))
        else:
            logger.warning("撤销委托失败, 无效的委托号或重复撤销的委托: %s" % str(order))

    def search_stocks(self, key, market="cn"):
        """
        搜索股票信息
        :param market: 股票市场: cn: 沪深, us: 美股, hk:港股
        :param key: 搜索关键字: 股票名称/代码/拼音
        :return:
        """
        key = urllib.parse.quote(key)
        assert market in ["cn", "us", "hk"]
        type = "111"  # cn
        if market == "us":
            type = "41"
        elif market == "hk":
            type = "31"
        url = "http://suggest3.sinajs.cn/suggest/type=%s&key=%s&name=suggestdata_%s" % (
            type, key, get_unix_timestamp()
        )
        r = self.session.get(url)
        return extract_stock_info(r.text)

    def get_stock_price(self, symbol):
        """
        获取股票当前价格
        :param symbol:
        :return:
        """
        url = "http://hq.sinajs.cn/list=s_%s" % symbol
        r = self.session.get(url)
        m = re.search(r'"(.*)"', r.text)
        if m and m.groups()[0]:
            name, price, _, _, _, _ = m.groups()[0].split(',')
            logger.info("股票[%s](%s)当前价格为: %s" % (name, symbol, price))
            return price
        else:
            logger.error("获取股票%s当前价格失败" % symbol)
            raise StockMatchError()

    # fixme: 该方法暂时只支持买入A股，不支持操作美股和港股
    @retry(wait_random_min=3000, wait_random_max=5000, retry_on_exception=retry_if_if_high_frequency)
    def buy(self, stock_code, amount=100, price=None):
        """
        买入股票, 该方法调用频率不能太快，调用频率不能高于3s/次
        :param stock_code: 股票代码
        :param price: 委托买入股票的价格，默认为股票当前价格
        :param amount: 买入股票数，必须为100的倍数
        :return:
        """
        assert amount >= 100 and amount % 100 == 0
        stocks = self.search_stocks(stock_code, market='cn')
        if len(stocks) != 1:
            raise StockMatchError("无法确定股票代码%s对应的股票。\r\n%s" % (stock_code, stocks))
        stock = stocks[0]
        if price is None:
            price = self.get_stock_price(stock['symbol'])

        url = "http://jiaoyi.sina.com.cn/api/jsonp_v2.php/jsonp_%s_%s/V2_CN_Order_Service.order" % (
            get_unix_timestamp(), get_random_string())

        r = self.session.get(url, params={
            "sid": self.uid,
            "cid": 10000,  # 该参数可能是比赛类型的参数，不同比赛时，该值可能不同
            "symbol": stock['symbol'],
            "price": price,
            "amount": amount,
            "type": "buy",
            "toweibo": 0,
            "enc": "utf8"
        })
        logger.info("准备买入股票[%s](%s), 买入价格: %s, 买入数量: %s" % (
            (stock['name'], stock['symbol'], price, amount)
        ))
        res = jsonp2dict(r.text)
        if isinstance(res, bool) and res:
            logger.info("下单成功")
        elif isinstance(res, dict):
            check_error(res)
        else:
            logger.error("未处理的返回情况: %s" % r.text)

    def _query_stock_hold(self, from_position=0, per_page=10):
        url = "http://jiaoyi.sina.com.cn/api/jsonp_v2.php/jsonp_%s_%s/V2_CN_Stockhold_Service.getStockhold" % (
            get_unix_timestamp(), get_random_string())
        r = self.session.get(url, params={
            "sid": self.uid,
            "cid": 10000,
            "count": per_page,
            "from": from_position
        })
        return jsonp2dict(r.text)

    def get_stock_hold(self):
        """
        获取当前持仓

        {
            "data": [
                {
                    "sg_id": "117989",
                    "contest_id": "10000",
                    "sid": "1768615155",
                    "zs_price": null,
                    "zy_price": null,
                    "HoldPercent": 0.6,   # 仓位
                    "StockCode": "sz000001",
                    "StockName": "平安银行",
                    "StockAmount": "200", # 当前持股
                    "AvailSell": "0",     # 可用股数
                    "TodayBuy": "200",
                    "TodaySell": "0",
                    "T4AvailSell": "0",
                    "T3AvailSell": "0",
                    "T2AvailSell": "0",
                    "T1AvailSell": "0",
                    "CurrentValue": null,
                    "cost": "14.920",    # 持仓成本
                    "StartDate": "2017-11-22 10:24:36",
                    "EndDate": "0000-00-00 00:00:00",
                    "mtime": "0000-00-00 00:00:00",
                    "CostFund": "2983.980", # 持仓花费金额
                    "newcost": 14.99,    # 最新价格
                    "dealvalue": "2983.980",
                    "newvalue": 2998,   # 持股市值
                    "profit": 14,       # 浮动盈亏
                    "profitRate": 0.47   # 盈亏比例
                }
            ],
            "count": "1",
            "status": "2"
        }
        """
        from_position = 0
        per_page = 10
        obj_stocks = []
        while True:
            json_stocks = self._query_stock_hold(from_position, per_page)
            for stock in json_stocks['data']:
                obj_stocks.append(json2obj(json.dumps(stock)))
            if from_position + per_page >= int(json_stocks['count']):
                break
            from_position += per_page

        return obj_stocks

    def sell(self, stock_code):
        """
        卖出股票
        :param stock_code:
        :return:
        """
        pass


if __name__ == "__main__":
    user = StockMatch(conf.SINA_CONFIG["username"], conf.SINA_CONFIG["password"])
    # stock_code = '000001'
    # user.buy(stock_code)
    # pretty_print(user.get_stock_hold())
    # print(len(user.get_today_orders()))
    # print(len(user.get_stock_hold()))
    for order in user.get_today_orders(status=OrderStatus.undealt):
        pretty_print_namedtuple(order)
