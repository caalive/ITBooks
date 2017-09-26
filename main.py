#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time : 17/09/10 1:10 PM
# Author : CA
import requests
import time
from bs4 import BeautifulSoup
import re
from multiprocessing import Process, Pool
import pymongo
from config import *
from AdditionalURL import *

header = {
'Host':'www.allitebooks.com',
'Upgrade-Insecure-Requests':'1',
'Cookie':'__atuvc=1%7C36%2C11%7C37; __atuvs=59b4c4d73bc32c18005; _ga=GA1.2.279602346.1504942122; _gid=GA1.2.567068390.1504942122; _gat=1',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'
}


class Property:
    def __init__(self, url='', rules='', selector='', headers=header, parser='lxml'):
        """
        :param url: 待爬取链接
        :param rules: 待爬取规则
        :param selector: 爬取选择器
        :param headers: 请求头
        :param parser: 解析器
        """
        self.url = url
        self.rules = rules
        self.selector = selector
        self.headers = headers
        self.parser = parser

    def get_html(self):
        """
        :return: 返回请求页面
        """
        response = requests.get(self.url, headers=self.headers)
        if response.status_code == requests.codes.ok:
            return response.text
        return None

    def _select_info(self, html, rules):
        """
        :param html: 待提取页面
        :param rules: 提取规则
        :return: 返回值形式为 [item1, item2 ... itemN]
        """
        if html and rules:
            soup = BeautifulSoup(html, self.parser)
            item = soup.select(rules)
            # 增加额外的URL链接到列表
            # 当传入规则为获取分类链接的规则时,提取url到列表.将自定义url加入列表
            if ADDITIONAL_URL and rules == 'ul.sub-menu > li > ul > li > a':
                item = [url.get('href') for url in item]
                item.extend(ADDITIONAL_URL)

            # temp为 获取的书籍下载链接
            temp = get_down_load_link(soup, down_link_rules)
            if temp:
                dttag = soup.new_tag("dt")
                #添加dt同级的dd标签
                ddtag = soup.new_tag("dd")

                #设置值
                new_string = soup.new_string("downloadlink: ")
                dttag.append(new_string)

                #将书籍的下载链接添加进去
                new_string = soup.new_string(temp[0].get('href'))
                ddtag.append(new_string)

                item[0].append(dttag)
                item[0].append(ddtag)
            for match in item:
                # yield 返回一个生成器,用for循环迭代
                yield match


    #这个函数暂时没有用
    def _mixed_info(self, html, rules):
        """
        :param html: 待提取页面
        :param rules: 提取规则
        :return: 返回值形式为 [item1, item2 ... itemN]
        """
        if html and rules:
            soup = BeautifulSoup(html, self.parser)
            for match in soup.find_all(rules):
                # yield 返回一个生成器,用for循环迭代
                yield match

    @staticmethod
    def _re_info(html, rules):
        """
        :param html: 待提取页面
        :param rules: 提取规则
        :return: 返回值形式为 [item1, item2 ... itemN]
        """
        if html and rules:
                pattern = re.compile(rules, re.S)
                match = pattern.findall(html)
                if match:
                    for item in match:
                        yield item
                else:
                    return None

    def get_info(self):
        html = self.get_html()
        if self.selector.lower() == 'select':
            if html:
                # print('use select selector')
                return self._select_info(html, self.rules)
        elif self.selector.lower() == 're':
            if html:
                # print('use re selector')
                return self._re_info(html, self.rules)

        elif self.selector.lower() == 'mix':
            if html:
                return self._mixed_info(html, self.rules)
        else:
            print('Please specify specific parser!!')

#所有书籍分类提取规则
categories_info_rules = 'ul.sub-menu > li > ul > li > a'

#该分类下所有书籍的概要信息提取规则
briefly_info_rules = r'<img.*?src="(.*?)".*?/>.*?<h2.*?<a href="(.*?)"\s*rel=.*?>(.*?)</a>.*?<h5 class="entry-author">.*?<a href="(.*?)".*?>(.*?)</a></h5>.*?<div\s*class="entry-summary".*?<p>(.*?)</p>'

#该分类名称(后面下载书籍时留作新建目录用以该分类作为文件夹名称)和该分类下所含书籍的总页数
total_page_rules = r'<h1.*?>(.*?)</h1>.*?<span class="pages">\d+ / (\d+) Pages</span>|<h1.*?>(.*?)</h1>'

#书籍的详细信息提取规则
detail_info_rules = r'div.book-detail > dl'

#下载链接提取规则
down_link_rules = r'span.download-links > a'

filterr = ['ASP.NET eBooks', 'CMS eBooks', 'HTML, HTML5 &amp; CSS eBooks', 'JavaScript eBooks']


"""

0. 类目名称                  <h1.*?>(.*?)</h1>
1. 书籍图片链接              .*?<img.*?src="(.*?)".*?/>
2. 书籍详细页链接            .*?<h2.*?<a href="(.*?)"\s*
3. 书籍名称                  rel=.*?>(.*?)</a>
4. 书籍作者链接              .*?<h5 class="entry-author">
5. 书籍作者                  .*?<a href="(.*?)".*?>(.*?)</a></h5>
6. 书籍描述                  .*?<div\s*class="entry-summary".*?<p>(.*?)</p>
7. 当前类目下书籍一共多少页   .*?title="Last Page &rarr;">(\d+)</a>
"""


#没使用,备用
def get_single_link(linklist):
    if isinstance(linklist, list):
        for item in linklist:
            yield item

#没使用,备用
def get_one_page_briefly(property, categorylink):
    subpage = property
    subpage.url = categorylink
    print(subpage.url)
    for item in subpage.get_info():
        print(item, len(item))

# 获取分类名称和总页数, 传入Property类实例
def get_dic_and_page(property):
    subpage = property
    catageinfo = subpage.get_info()
    if catageinfo:
        for item in catageinfo:
            if item[-1] and item[-1] != 'No Posts Found.':  # 元组最后一项不为空且不等于 'No Posts Found.'
                directory, total_page_numbers = re.sub(r'^\.', '', item[-1]), '1'  # 将以点开头的目录名 去掉点
                return directory.strip(), total_page_numbers.strip()
            elif item[0]: # 首元素不为空
                directory, total_page_numbers, _ = item
                return re.sub(r'^\.', '', directory.strip()), total_page_numbers.strip()
    else:
        return None

# 产生该分类下每一页的链接
def generate_page_link(linkseed, start, end='', suffix=''):
    for link in [linkseed + suffix + '{}'.format(str(i)) for i in range(int(start), int(end) + 1)]:
        yield link

# 获取下载链接
def get_down_load_link(soup, rules=''):
    match = soup.select(rules, limit=1)
    return match


# 封装数据,返回该分类下的所有书籍的详细信息 {category:[{book1},{book2}...]}
def get_en_data():
    pass


# 保存数据到mongodb
def save_to_mongo(result, cobj):
    if cobj.get_collection().update({}, {'$pushAll': {list(result.keys())[0].replace('.', '_'): list(result.values())[0]}}, upsert=True):
        print('存储到MongoDB成功')
        return True
    return False


# curcate(current categories)为当前采集到的书籍类目 format : (类目名, 当前类目下的书籍页数)
# dbcate(database categories)为从数据库中查询到的书籍类目 format : {'类目1': '该类目对应的书籍总数'.....}
# 比较当前类目和当前类目对应的书籍页数是否和数据库查询回来的类目相同
# 类目存在,页数不同则设置为查询回来的页数
# 如果类目不存在,页数为当前类目采集的页数
# 这个函数写的有点烂,不要骂我,呵呵哒 O(∩_∩)O~
# 一个函数返回三个状态,醉了....

def compare_cate_and_set_number(curcate, dbcate):
    if isinstance(curcate, tuple) and isinstance(dbcate, dict):
        key = curcate[0].replace('.', '_')
        # print(key, dbcate.keys())
        if key in dbcate.keys():
            if int(curcate[1]) == int(dbcate[key]) // 10 + 1:  # 每页10条,除以10算出总页数,除不尽则 + 1
                return 'FULL COMPARE'
            else:
                return int(dbcate[key]) // 10 + 1
        else:
            return None

# main(cobj) --> cobj为当前数据库表的对象
def main(cobj):
    mainentrance = 'http://www.allitebooks.com/'
    mainpage = Property(mainentrance, categories_info_rules, 'select')
    kv = cobj.get_cate_and_index()
    # 分类目录链接循环
    for categoryurl in mainpage.get_info():
        # print(categoryurl)
        # continue
        subpage = Property(categoryurl, total_page_rules, 're')
        # 获取单个分类名称和总页数
        # continue
        result = get_dic_and_page(subpage)
        # print(result)
        # 是无效的页面,就跳过去
        if not result:
            continue
        current_number = [1]
        directory, total_page_numbers = result
        print(directory, total_page_numbers)

        # 返回当前collection(表中)现有书籍类目的名称,和该书籍类目所对应的条数
        su = compare_cate_and_set_number(result, kv)
        if 'FULL COMPARE' == su:
            continue
        elif not su:
            pass
        else:
            current_number[0] = su

        # if(directory != 'MongoDB eBooks'):
        #     continue

        # briefly_info_rules 单个分类下,所有书籍概要信息提取规则
        subpage.rules = briefly_info_rules

        # 单个分类下每一页,页索引 -> link
        for link in generate_page_link(subpage.url, current_number[0], total_page_numbers, r'page/'):
            subpage.url = link
            subpage.rules = briefly_info_rules
            subpage.selector = 're'
            # print(subpage.url)

            print('第 ' + subpage.url[len(subpage.url) - 2:] + ' 页')
            # subpage.selector = 're'
            pageinfo = []
            # 单个分类下每一页书籍概要信息循环
            for info in subpage.get_info():
                # print(info)
                subpage.url = info[1]
                print(subpage.url)
                subpage.rules = detail_info_rules
                subpage.selector = 'select'
                datailinfo = {}

                for i in subpage.get_info():  #书籍详细信息获取
                    temp = i.text.split('\n') #换行符分隔字符串
                    for items in temp:
                        if items:            #字符串不为空
                            key, value = items.split(':', maxsplit=1)   # 以冒号分隔(分隔一次,全部分隔会报错),生成字典
                            datailinfo[key.strip()] = value.strip()   #每本书详细信息字典列表
                    pageinfo.append(datailinfo)

            if pageinfo:
                save_to_mongo({directory: pageinfo}, cobj)  # 将书籍详细信息加入数据库

            # print(pageinfo)
                    # return

        # return


class DownLoader:
    pass


class DataBaseOP:
    def __init__(self, host=None, database=None, collection=None):
        self._hostname = host
        self._database = database
        self._collection = collection

    def get_collection(self):
        # 创建数据库链接, 返回指定的collection对象
        client = pymongo.MongoClient(self._hostname)
        table = client[self._database]
        return table[self._collection]

    # 返回当前collection(表中)现有书籍类目的名称,和该书籍类目所对应的条数
    def get_cate_and_index(self):
        table = self.get_collection()
        item = table.find_one()
        kv = dict()
        for key in item.keys():
            if key != '_id':
                kv[key] = len(item[key])
        return kv


if __name__ == '__main__':
    collection = DataBaseOP(MONGO_URL, MONGO_DB, MONGO_TABLE)
    main(collection)


