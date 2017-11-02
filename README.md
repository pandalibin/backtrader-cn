## backtrader-cn

[![Build Status](https://travis-ci.org/pandalibin/backtrader-cn.svg?branch=master)](https://travis-ci.org/pandalibin/backtrader-cn)
[![Coverage Status](https://codecov.io/gh/pandalibin/backtrader-cn/branch/master/graph/badge.svg)](https://codecov.io/gh/pandalibin/backtrader-cn)
[![Doc Status](https://readthedocs.org/projects/backtrader-cn/badge/?version=latest)](http://backtrader-cn.readthedocs.io/en/latest/?badge=latest)

### 快速上手

#### 下载代码

	$ git clone https://github.com/pandalibin/backtrader-cn.git

#### 安装 `mongodb`

##### Mac OSX

	$ brew install mongodb
	$ brew services start mongodb

##### Ubuntu/Debian

	$ sudo apt-get install mongodb

安装 Python modules

	$ pip install -U -r requirements.txt

获取股票数据

	$ python data_main.py

计算入场信号

	$ python frm_main.py
