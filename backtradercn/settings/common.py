# -*- coding: utf-8 -*-
import os

PROJECT_NAME = 'backtradercn'

# log setting
LOG_DIR = '/tmp/'
LOG_LEVEL = 'DEBUG'

# database setting
MONGO_HOST = 'localhost'
CN_STOCK_LIBNAME = 'ts_his_lib'
DAILY_STOCK_ALERT_LIBNAME = 'daily_stock_alert'
STRATEGY_PARAMS_LIBNAME = 'strategy_params'

# wechat
WECHAT_APP_ID = 'wx5e8e3c4779887f32'
WECHAT_APP_SECRET = 'd4624c36b6795d1d99dcf0547af5443d'

# xueqiu account
XQ_ACCOUNT = os.getenv('XQ_ACCOUNT', '18628391725')
XQ_PASSWORD = os.getenv('XQ_PASSWORD', 'gupiao888')
XQ_PORTFOLIO_MARKET = os.getenv('XQ_PORTFOLIO_MARKET', 'cn')
# 默认的组合前缀，组合名称格式为 组合前缀 + 股票代码
# 组合名字
XQ_CUBES_PREFIX = 'SC'
# 默认创建组合时股票的初始百分数
XQ_DEFAULT_BUY_WEIGHT = 5
