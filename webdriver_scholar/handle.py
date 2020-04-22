# coding: utf8
from time import time
from utils import mysleep, http, Scholar, Mypath, Scihub, http_webdrive, webdrive_init, renji_check, Scholar4Webdriver
from settings import BASE_DIR, log, args, ILLEGAL_CHAR
from db import get_db
import json
from re import sub
from time import sleep
from multiprocessing import Pool
from config import scihub_config, mode_config


class Handler(Scholar4Webdriver):
    def __init__(self):
        self.keys = self.get_search_keys()
        self.max_page = int(args.maxpage)
        try:
            self.sci = Scihub()
        except RuntimeError:
            self.sci = None
    
    def download_paper(self, r, mypath, key):
        db = get_db()
        r['title'] = sub(ILLEGAL_CHAR, '', r['title'])
        pdf, cur_url = r['url']
        # check repeat
        check = db.execute(
            'SELECT * FROM paper'
            ' WHERE title = ? AND paper_url = ?',
            (r['title'], cur_url)
            ).fetchall()
        if check:
            log.logger.info(f"{r['title']}======此文献信息已存在数据库中")
            r['downloaded'] = 'repeat'
            r['url'] = cur_url
            r['file_path'] = 'repeat'
            return
        # 如果当前url是pdf链接，直接进行下载
        if pdf is True:
            r['downloaded'] = mypath.save(cur_url, r['title'])
        # 通过sci-hub获取下载地址
        # 这一步的情况包括：直接下载pdf失败的、目标地址不是pdf的
        if r['downloaded'] is False and (self.sci is not None or args.scihub):
            if args.scihub:
                sci_url = args.scihub
            else:
                sci_url = self.sci.get(cur_url)
            r['downloaded'] = mypath.save(sci_url, r['title'])

        r['keyword'] = key
        r['url'] = cur_url
        r['file_path'] = str(mypath.to_pdf_path(r['title']))
        # 返回结果，最后再统一操作数据库，避免插入的时候id冲突
        return r
    
    def insert_db(self, data_list):
        db = get_db()
        for r in data_list:
            db.execute(
            'INSERT INTO paper (title, downloaded, paper_url, key_words, pdf_path, author, quote, pubtime, ner_res)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (r['title'], str(r['downloaded']), r['url'],r['keyword'],r['file_path'],r['author'],r['qoute'],r['pubtime'],'None')
            )
            db.commit()
        #db.close()


    def run(self):
        browser = webdrive_init()
        if self.keys[-1] == '':
            self.keys.pop()
        for key in self.keys:
            max_page = self.max_page
            #key = sub(ILLEGAL_CHAR, '', key)
            #keyword = "_".join(key.split())
            data = []
            #print(f'\n关键词：{key}')
            """ 读取关键词 """
            key = key.strip()
            url = self.get_first_url(key)
            #print(url)
            mypath = Mypath(key)
            #
            http_webdrive(url, browser)
            page_flag = True
            while True:
                """ 获取当前关键词的所有数据 """
                html = browser.page_source
                while renji_check(html):
                    html = browser.page_source
                #html = http(url)
                #log.logger.info(f'搜索结果:{html}')
                log.logger.info(f"===++===page===++===:::{max_page}")
                page_flag, max_page, records = self.get(browser, max_page)
                #print(records)
                # downloading PDF
                if scihub_config['multiprocessing'] and len(records) > 1:
                    p = Pool(len(records))
                    result = []
                    for r in records:
                        result.append(p.apply_async(self.download_paper, args=(r, mypath, key)))
                    p.close()
                    p.join()
                    # 将结果插入数据库
                    data_list = []
                    for i in result:
                        if i.get():
                            data_list.append(i.get())
                    if data_list:
                        self.insert_db(data_list)
                elif records:
                    print("没有在并行下载")
                    for r in records:
                        result = self.download_paper(r, mypath, key)
                    if result:
                        self.insert_db([result])
                
                data += records
                #mysleep()
                """ 当前关键词查询结束，换下一下 """
                if not page_flag or max_page == 0:
                    break
                #mysleep()
            #browser.quit()
            if len(data) != 0:
                res = mypath.save_result(key, data)
        browser.quit()
        return

    def get_search_keys(self):
        """ 读取关键词 """
        if args.keys:
            if mode_config['keywordfile']:
                with open(args.keys, 'r') as fn:
                    return fn.read().split('\n')
            # 修改成直接传字符串
            else:
                return args.keys.split(',')
        else:
            print("no key words")



def main():
    h = Handler()
    return h.run()


if __name__ == "__main__":
    log.logger.info('任务开始')
    start_at = time()
    #print(main())
    main()
    log.logger.info(f'任务结束，耗时{time() - start_at}s')
