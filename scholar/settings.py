from pathlib import Path
from logging import basicConfig, INFO, getLogger
from requests import Session

from fake_useragent import UserAgent
from requests.exceptions import (ReadTimeout as rReadTimeout, ConnectTimeout,
                                 ConnectionError)
from http3.exceptions import PoolTimeout, ReadTimeout as hReadTimeout
from h2.exceptions import StreamClosedError, ProtocolError
from h11._util import RemoteProtocolError
from argparse import ArgumentParser

basicConfig(level=INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = getLogger(__name__)

ua = UserAgent(cache=True)
sess = Session()
sess.headers['User-Agent'] = ua.random

parser = ArgumentParser(description='文献自动爬取装置')
parser.add_argument('--datadir', help='数据文件目录的绝对路径')
parser.add_argument('--timeout', help='休眠时长，单位秒')
parser.add_argument('--mirror', help='自定义谷歌学术镜像网站')
parser.add_argument('--keys', help='搜索关键词文本文件绝对路径')
parser.add_argument('--scihub', help='自定义sci-hub下载网站')
parser.add_argument('--maxpage', help='自定义搜索页面数目')
args = parser.parse_args()

# 当前文件的父级目录
BASE_DIR = Path(__file__).parent.absolute()

if args.datadir:
    DATA_DIR = Path(args.datadir).absolute() / 'data'
else:
    DATA_DIR = BASE_DIR / 'data'
# 如果数据文件不存在，则创建
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 设置谷歌学术搜索链接
if args.mirror:
    BASE_URL = args.mirror
else:
    BASE_URL = 'https://scholar.google.com.hk'
# 超时时长，单位秒，停止时间为均值为SLEEP_TIME，方差为SLEEP_TIME/4的正态分布
SLEEP_TIME = int(args.timeout) if args.timeout else 10

# 异常集合
EXCEPTION = (rReadTimeout, ConnectTimeout, PoolTimeout, hReadTimeout,
             StreamClosedError, ProtocolError, RemoteProtocolError,
             ConnectionError)
# 匹配路径中的非法字符
ILLEGAL_CHAR = r'[\\/:*?"<>()|\r\n\.]+'
