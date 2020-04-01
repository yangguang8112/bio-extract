# coding: utf8
from time import time
from utils import mysleep, http, Scholar, Mypath, Scihub, http_webdrive
from settings import BASE_DIR, log, args, ILLEGAL_CHAR
from db import get_db
import json
from re import sub
from time import sleep


class Handler(Scholar):
    def __init__(self):
        self.keys = self.get_search_keys()
        self.max_page = int(args.maxpage)
        try:
            self.sci = Scihub()
        except RuntimeError:
            self.sci = None

    def run(self):
        # 连接数据库
        db = get_db()
        max_page = self.max_page
        for key in self.keys:
            #key = sub(ILLEGAL_CHAR, '', key)
            #keyword = "_".join(key.split())
            data = []

            #print(f'\n关键词：{key}')
            """ 读取关键词 """
            url = self.get_first_url(key)
            #print(url)
            mypath = Mypath(key)
            while True:
                """ 获取当前关键词的所有数据 """
                #html = http_webdrive(url)
                html = http(url)
                #log.logger.info(f'搜索结果:{html}')
                log.logger.info(f"===++===page===++===:::{max_page}")
                url, max_page, records = self.get(html, max_page)
                for r in records:
                    r['title'] = sub(ILLEGAL_CHAR, '', r['title'])
                    pdf, cur_url = r['url']
                    # check repeat
                    check = db.execute(
                        'SELECT * FROM paper'
                        ' WHERE title = ? AND paper_url = ?',
                        (r['title'], cur_url)
                    ).fetchall()
                    if check:
                        r['downloaded'] = 'repeat'
                        r['url'] = cur_url
                        r['file_path'] = 'repeat'
                        continue
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
                    #
                    db.execute(
                        'INSERT INTO paper (title, downloaded, paper_url, key_words, pdf_path, author, quote, pubtime, ner_res)'
                        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (r['title'], str(r['downloaded']), r['url'],r['keyword'],r['file_path'],r['author'],r['qoute'],r['pubtime'],'None')
                        )
                    db.commit()
                    mysleep()

                data += records
                #mysleep()
                """ 当前关键词查询结束，换下一下 """
                if not url or max_page == 0:
                    break
                #mysleep()
            if len(data) == 0:
                return
            
            res = mypath.save_result(key, data)
            return res

    def get_search_keys(self):
        """ 读取关键词 """
        if args.keys:
            #with open(args.keys, 'r', encoding='utf8') as fn:
            #    return fn.read().split('\n')
            # 修改成直接传字符串
            return args.keys.split(',')
        else:
            with open(BASE_DIR / 'keys.txt', 'r', encoding='utf8') as fn:
                return fn.read().split('\n')



def main():
    h = Handler()
    return h.run()


if __name__ == "__main__":
    log.logger.info('任务开始')
    start_at = time()
    #print(main())
    main()
    log.logger.info(f'任务结束，耗时{time() - start_at}s')
