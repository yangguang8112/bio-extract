import numpy as np
from re import split, sub, search
from time import sleep

from settings import (BASE_URL, DATA_DIR, log, SLEEP_TIME, EXCEPTION,
                      ILLEGAL_CHAR, sess)
from pandas import DataFrame
from lxml.html import fromstring
from lxml.etree import ParserError

import json
from config import chrome_config, scihub_config


def mysleep(ms: int = SLEEP_TIME) -> None:
    mu = ms
    sigma = ms / 4
    ms2 = abs(int(np.random.normal(mu, sigma)))
    log.logger.info(f'休眠{ms2}s')
    sleep(int(ms2))
    #logger.info(f'休眠2s')
    #sleep(2)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
#chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--user-data-dir="+chrome_config['web_user_data'])

def renji_check(html):
    if '请进行人机身份验证' in html or '我们的系统检测到您的计算机网络中存在异常流量' in html:
        puase = input("请进行人机验证，验证后按任意键继续:")
        return 1
    return 0

def webdrive_init():
    browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_config['webdriver_path'])
    browser.set_page_load_timeout(1000000)
    return browser

def index_page(url, browser, *, timeout: int = 20, auto_reload: int = 1):
    log.logger.info(f'访问 {url}')
    mysleep(3)
    try:
        browser.get(url)
        sleep(5)
        html = browser.page_source
        if '请进行人机身份验证' in html or '我们的系统检测到您的计算机网络中存在异常流量' in html:
            puase = input("请进行人机验证，验证后按任意键继续:")
            html_check = browser.page_source
            if '请进行人机身份验证' in html_check or not html_check or '我们的系统检测到您的计算机网络中存在异常流量' in html:
                print("进了二次验证")
                browser.quit()
                sleep(5)
                return index_page(url,browser,timeout=timeout,auto_reload=auto_reload)
            else:
                return browser
        if not html:
            browser.quit()
            puase = input("页面什么都没有，查看原因后按任意键继续:")
            return index_page(url,browser,timeout=timeout,auto_reload=auto_reload)
        return browser
    except EXCEPTION as e:
        #暂时先不用重新请求
        print("请求出错")
        print(e)
        auto_reload = 0
    if auto_reload == 0:
        browser.quit()
        return
    browser.quit()
    mysleep(timeout)
    return index_page(url,browser,timeout=timeout,auto_reload=auto_reload)

def search_key(browser, key_word):
    log.logger.info(f'正在查询关键词 {key_word}')
    search_field = browser.find_element_by_name('q')
    search_field.clear()
    search_field.send_keys(key_word)
    sleep(3)
    search_field.submit()
    html = browser.page_source
    while renji_check(html):
        html = browser.page_source
    return browser

def http_webdrive(url, browser, *, timeout: int = 20, auto_reload: int = 1):
    #print("zheli")
    log.logger.info(f'访问 {url}')
    mysleep(3)
    #browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_config['webdriver_path'])
    #browser = webdriver.Chrome(chrome_options=chrome_options)
    try:
        browser.get(url)
        # 需要等浏览器反应一下，不然会返回奇怪的page_source不过和服务器访问的时候返回的一样
        sleep(5)
        html = browser.page_source
        # webdriver无法获取状态码，后期看能不能从页面中找到一些关键信息
        #logger.info(f'{browser.title}')
        if '请进行人机身份验证' in html or '我们的系统检测到您的计算机网络中存在异常流量' in html:
            print("aaaaaaaaaaaaaaaaaa======================")
            #check_brow = renji_check(url)
            puase = input("请进行人机验证，验证后按任意键继续:")
            html_check = browser.page_source
            if '请进行人机身份验证' in html_check or not html_check or '我们的系统检测到您的计算机网络中存在异常流量' in html:
                print("进了二次验证")
                browser.quit()
                sleep(5)
                return http_webdrive(url,browser,timeout=timeout,auto_reload=auto_reload)
            else:
                #browser.quit()
                return browser
        if not html:
            browser.quit()
            print("页面什么都没有，快去查看原因")
            return http_webdrive(url,browser,timeout=timeout,auto_reload=auto_reload)
        #browser.quit()
        return browser
    except EXCEPTION as e:
        #暂时先不用重新请求
        print("请求出错")
        print(e)
        auto_reload = 0
    if auto_reload == 0:
        browser.quit()
        return
    browser.quit()
    mysleep(timeout)
    return http_webdrive(url,browser,timeout=timeout,auto_reload=auto_reload)

def http(
        url,
        *,
        rept: str = 'text',  # 返回类型
        method: str = 'get',  # 请求方法
        timeout: int = 20,  # 默认超时时间20s
        params: dict = None,  # 请求参数
        headers: dict = None,  # 请求头
        auto_reload: int = 1):  # 遇到错误自动重新发起请求次数

    assert isinstance(rept, str)
    assert isinstance(method, str)
    rept = rept.lower()
    method = method.lower()
    assert rept in ('text', 'bytes', 'json', 'obj')
    assert method in ('get', 'post', 'put', 'delete')

    log.logger.info(f'{method} {url}')
    try:
        #r = getattr(sess, method)(url, headers=headers, params=params,timeout=timeout)
        r = getattr(sess, method)(url, headers=headers, params=params,timeout=(18,15))
        if r.status_code == 200:
            if rept == 'obj':
                return r
            if rept == 'text':
                return r.text
            if rept == 'bytes':
                return r.content
            return r.json()
        if r.status_code == 404:
            auto_reload = 0
        # 该状态码表明网站有封闭ip的可能，无需重复请求了
        if r.status_code == 429:
            auto_reload = 0
        log.logger.warn(f'请求失败状态码 {r.status_code}')
    except EXCEPTION as e:
        #print(e)
        if auto_reload == 0:
            log.logger.warn(f'错误无法通过重发请求解决')
        else:
            log.logger.info(f'网络错误 尝试重发请求')
    except Exception as e:
        log.logger.error(f'未知错误 {e}')
    if auto_reload == 0:
        return None
    auto_reload -= 1
    #mysleep(timeout)
    return http(url,
                rept=rept,
                method=method,
                params=params,
                timeout=timeout,
                headers=headers,
                auto_reload=auto_reload)

class Scholar4Webdriver:
    def get(self, browser, max_page_num) -> tuple:
        html = browser.page_source
        if not html:
            #puase = input("页面没有内容，请检查页面，如果没有问题请输入1，则程序会结束，否则请刷新浏览器后输入0:")
            #if int(pause) == 1
            #return '', 0, []
            # 直接自动刷新页面
            log.logger.info(f"页面无内容，刷新页面，链接为:::{browser.current_url}")
            browser.refresh()
            return self.get(browser, max_page_num)
        tree = fromstring(html)
        divs = tree.xpath('//div[@id="gs_res_ccl_mid"]/div')
        #node = tree.xpath('//div[@id="gs_n"]//td')
        #print(tree)
        # 看是否还有下一页
        try:
            next_button = browser.find_element_by_link_text('下一页')
        except:
            next_button = None

        if not divs:
            # 这里应该是搜索结果为0
            #puase = input("页面没有内容，请检查页面，如果没有问题按任意键继续:")
            return None, 0, []
        
        nurl = None
        #if not node:
        log.logger.info(f"======page======:::{max_page_num}")
        log.logger.info(f"当前访问的页面链接为:::{browser.current_url}")
        if next_button and max_page_num > 0:
            #return None, []
            #当有下一页的时候才翻页，否则nurl为None
            max_page_num -= 1
            mysleep(5)
            next_button.click()
        else:
            #puase = input("没有找到下一页，请检查页面，如果没有问题按任意键继续:")
            try:
                next_button = browser.find_element_by_link_text('下一页')
            except:
                log.logger.info("======没有达到最大页输出，请核查是否确实搜索结果不足最大页数======")
            #max_page_num = 0
        log.logger.info(f"======page======:::{max_page_num}")
        
        #nurl = self.get_next_url(node[-1])

        # 这里同时返回了下一页的地址，当前页的数据
        #log.logger.info(f"scholar get返回值:::{nurl},{max_page_num}")
        return True if next_button else None, max_page_num, [{
            'title':
                self.get_title(d.xpath('.//h3[@class="gs_rt"]')),
            'author':
                self.get_author(d.xpath('.//div[@class="gs_a"]')),
            'qoute':
                self.get_qoute(
                    d.xpath(
                        './/div[@class="gs_fl"]/a[contains(string(.), "被引用")]')),
            'pubtime':
                self.get_pubtime(d.xpath('.//div[@class="gs_a"]/text()')),
            'downloaded':
                False,
            'url':
                self.get_url(d.xpath('.//span[@class="gs_ct1"]/text()'),
                             d.xpath('.//h3[@class="gs_rt"]/a'),
                             d.xpath('.//span[@class="gs_ctg2"]/text()'),
                             d.xpath('.//div[@class="gs_or_ggsm"]/a'))
        } for d in divs if d.xpath('.//h3[@class="gs_rt"]/a')]

    @staticmethod
    def get_title(node) -> str:
        if len(node) == 0:
            return ''
        t = node[0].xpath('string(.)')
        t = sub(r'(\n|PDF|HTML|\[|\])', '', t)
        return t.strip()

    @staticmethod
    def get_author(node) -> str:
        if len(node) == 0:
            return ''
        return split(r'[-…]', node[0].xpath('string(.)'))[0]

    @staticmethod
    def get_qoute(node) -> int:
        if len(node) == 0:
            return 0
        return int(sub(r'\D+', '', node[0].text))

    @staticmethod
    def get_pubtime(node) -> str:
        if len(node) == 0:
            return ''
        _ = search(r'(?P<p>\d{4})', ''.join(node))
        return _.group('p') if _ else ''

    @staticmethod
    def get_url(*nodes) -> str:
        # 先对居中位置的搜索结果进行pdf判断
        # 如果是pdf，直接返回链接
        if bool(nodes[0]) and 'pdf' in nodes[0][0].lower():
            return True, nodes[1][0].attrib['href']

        # 上述没有结果
        # 再对右边栏进行pdf搜索，如果有pdf资源，直接返回链接
        if bool(nodes[2]) and 'pdf' in nodes[2][0].lower():
            return True, nodes[3][0].attrib['href']

        # 直接判断地址是否为pdf链接
        if nodes[1]:
            url = nodes[1][0].attrib['href']
            return url.endswith('.pdf'), url
        # 标题为引用的情况下，是没有地址的
        else:
            return False, None

    @staticmethod
    def get_first_url(key: str) -> str:
        #q = '+'.join(split(r's+', key or ''))
        # 为什么要把s去掉换成空格？？？？？？
        q = '+'.join(key.split(' '))
        return f'{BASE_URL}/scholar?start=0&q={q}&hl=zh-CN&as_sdt=0,44'

    @staticmethod
    def get_next_url(tree, max_page) -> tuple:
        if len(tree) == 0 or max_page == 0:
            return ''
        # 判断是否有“下一页”这个按钮，
        # 如果有hidden，表示按钮隐藏，当前页即是末页
        if 'hidden' in tree.xpath('.//b')[0].attrib['style']:
            return ''
        max_page -= 1
        return (tree.xpath('./a')[0].attrib['href'], max_page)

class Scholar:
    def get(self, html: str, max_page_num) -> tuple:
        if not html:
            return '', 0, []
        tree = fromstring(html)
        divs = tree.xpath('//div[@id="gs_res_ccl_mid"]/div')
        node = tree.xpath('//div[@id="gs_n"]//td')
        #print(tree)

        if not divs:
            return None, 0, []
        
        nurl = None
        #if not node:
        log.logger.info(f"======page======:::{max_page_num}")
        if node and max_page_num > 0:
            #return None, []
            #当有下一页的时候才翻页，否则nurl为None
            nurl, max_page_num = self.get_next_url(node[-1], max_page_num)
        else:
            max_page_num = 0
        log.logger.info(f"======page======:::{max_page_num}")
        
        #nurl = self.get_next_url(node[-1])

        # 这里同时返回了下一页的地址，当前页的数据
        #log.logger.info(f"scholar get返回值:::{nurl},{max_page_num}")
        return f'{BASE_URL}{nurl}' if nurl else None, max_page_num, [{
            'title':
                self.get_title(d.xpath('.//h3[@class="gs_rt"]')),
            'author':
                self.get_author(d.xpath('.//div[@class="gs_a"]')),
            'qoute':
                self.get_qoute(
                    d.xpath(
                        './/div[@class="gs_fl"]/a[contains(string(.), "被引用")]')),
            'pubtime':
                self.get_pubtime(d.xpath('.//div[@class="gs_a"]/text()')),
            'downloaded':
                False,
            'url':
                self.get_url(d.xpath('.//span[@class="gs_ct1"]/text()'),
                             d.xpath('.//h3[@class="gs_rt"]/a'),
                             d.xpath('.//span[@class="gs_ctg2"]/text()'),
                             d.xpath('.//div[@class="gs_or_ggsm"]/a'))
        } for d in divs if d.xpath('.//h3[@class="gs_rt"]/a')]

    @staticmethod
    def get_title(node) -> str:
        if len(node) == 0:
            return ''
        t = node[0].xpath('string(.)')
        t = sub(r'(\n|PDF|HTML|\[|\])', '', t)
        return t.strip()

    @staticmethod
    def get_author(node) -> str:
        if len(node) == 0:
            return ''
        return split(r'[-…]', node[0].xpath('string(.)'))[0]

    @staticmethod
    def get_qoute(node) -> int:
        if len(node) == 0:
            return 0
        return int(sub(r'\D+', '', node[0].text))

    @staticmethod
    def get_pubtime(node) -> str:
        if len(node) == 0:
            return ''
        _ = search(r'(?P<p>\d{4})', ''.join(node))
        return _.group('p') if _ else ''

    @staticmethod
    def get_url(*nodes) -> str:
        # 先对居中位置的搜索结果进行pdf判断
        # 如果是pdf，直接返回链接
        if bool(nodes[0]) and 'pdf' in nodes[0][0].lower():
            return True, nodes[1][0].attrib['href']

        # 上述没有结果
        # 再对右边栏进行pdf搜索，如果有pdf资源，直接返回链接
        if bool(nodes[2]) and 'pdf' in nodes[2][0].lower():
            return True, nodes[3][0].attrib['href']

        # 直接判断地址是否为pdf链接
        if nodes[1]:
            url = nodes[1][0].attrib['href']
            return url.endswith('.pdf'), url
        # 标题为引用的情况下，是没有地址的
        else:
            return False, None

    @staticmethod
    def get_first_url(key: str) -> str:
        #q = '+'.join(split(r's+', key or ''))
        # 为什么要把s去掉换成空格？？？？？？
        q = '+'.join(key.split(' '))
        return f'{BASE_URL}/scholar?start=0&q={q}&hl=zh-CN&as_sdt=0,44'

    @staticmethod
    def get_next_url(tree, max_page) -> tuple:
        if len(tree) == 0 or max_page == 0:
            return ''
        # 判断是否有“下一页”这个按钮，
        # 如果有hidden，表示按钮隐藏，当前页即是末页
        if 'hidden' in tree.xpath('.//b')[0].attrib['style']:
            return ''
        max_page -= 1
        return (tree.xpath('./a')[0].attrib['href'], max_page)


class Scihub:
    def __init__(self):
        self.base_urls = self._get_available_urls()
        self.base_url = self.base_urls[0]

    def get(self, url: str) -> str:
        if not url:
            return None
        url = f'{self.base_url}/{url}'
        #return None
        html = http(url)
        if html is None:
            return None

        try:
            tree = fromstring(html)
        except (ParserError, ValueError) as e:
            log.logger.error(f'有可能被sci-hub或者资源网站封了IP {e}')
            return None

        node = tree.xpath('.//iframe[@id="pdf"]')
        if len(node) == 0:
            return None
        url = node[0].attrib['src']
        if url.startswith('http'):
            return url
        return f'https:{url}'

    def _get_available_urls(self) -> list:
        url = 'https://sci-hub.now.sh/'
        #url = 'http://tool.yovisun.com/scihub/'
        '''
        html = http(url, rept='text')

        if html is None:
            raise RuntimeError('没有可用的sci-hub地址')

        tree = fromstring(html)
        node = tree.xpath('.//a[contains(@href, "//sci-hub.")]')
        urls = [i.attrib['href'] for i in node]
        if len(urls) == 0:
            raise RuntimeError('没有可用的sci-hub地址')
        '''
        urls = scihub_config['url_list'].split(',')
        return urls


class Mypath:
    def __init__(self, folder: str):
        folder = "_".join(folder.split(' '))
        self.folder = DATA_DIR / sub(ILLEGAL_CHAR, '', folder)
        self.folder.mkdir(parents=True, exist_ok=True)

    def save(self, url, fname) -> bool:
        if url is None:
            return False

        fname = self.to_pdf_path(fname)
        if fname.exists():
            log.logger.info(f'文件已存在 {fname.name}')
            return True

        r = http(url, rept='obj')
        if r is None:
            log.logger.info(f'下载失败 {url}')
            return False

        try:
            with open(fname, 'wb') as fn:
                for chunk in r.iter_content(8192):
                    fn.write(chunk)
            return True
        except Exception as e:
            log.logger.error(f'写入错误 {e}')
            return False

    def save_result(self, key: str, data: dict) -> None:
        if not data:
            log.logger.warning(f'关键词{key} 没有搜索结果')
            return
        key = "_".join(key.split(' '))
        fname = sub(ILLEGAL_CHAR, '', key)
        xlsx_fname = DATA_DIR / f'{fname}.xlsx'
        df = DataFrame.from_records(data)
        #df.to_excel(xlsx_fname, index=None)
        #改成json格式方便后面直接放到数据库
        fname = DATA_DIR / f'{fname}.json'
        with open(fname,'w') as fn:
            json.dump(data, fn)
        return str(fname)
        log.logger.info(f'saved to {fname.name}')

    def to_pdf_path(self, fname: str):
        fname = "_".join(fname.split(' '))
        fname = sub(ILLEGAL_CHAR, '', fname)
        return self.folder / f'{fname}.pdf'
