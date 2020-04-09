from pathlib import Path
###更新2020/03/04
# from logging import basicConfig, INFO, getLogger
#更改一下log函数，将log保存在目录下
import logging
from logging import handlers
###
from requests import Session

from fake_useragent import UserAgent
from requests.exceptions import (ReadTimeout as rReadTimeout, ConnectTimeout,
                                 ConnectionError)
from http3.exceptions import PoolTimeout, ReadTimeout as hReadTimeout
from h2.exceptions import StreamClosedError, ProtocolError
from h11._util import RemoteProtocolError
from argparse import ArgumentParser

###更新2020/03/04
#basicConfig(level=INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
#logger = getLogger(__name__)
class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }  # 日志级别关系映射

    def __init__(self, filename, level='info', when='D', backCount=3,
                 fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)  # 设置日志格式
        self.logger.setLevel(self.level_relations.get(level))  # 设置日志级别
        sh = logging.StreamHandler()  # 往屏幕上输出
        sh.setFormatter(format_str)  # 设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount,
                                               encoding='utf-8')  # 往文件里写入#指定间隔时间自动生成文件的处理器
        # 实例化TimedRotatingFileHandler
        # interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setFormatter(format_str)  # 设置文件里写入的格式
        self.logger.addHandler(sh)  # 把对象加到logger里
        self.logger.addHandler(th)

log = Logger('all.log', level='debug')

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
