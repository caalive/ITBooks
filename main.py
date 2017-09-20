#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time : 17/09/10 1:10 PM
# Author : CA
import requests
import time
from bs4 import BeautifulSoup
import re

header = {
'Host':'www.allitebooks.com',
'Upgrade-Insecure-Requests':'1',
'Cookie':'__atuvc=1%7C36%2C11%7C37; __atuvs=59b4c4d73bc32c18005; _ga=GA1.2.279602346.1504942122; _gid=GA1.2.567068390.1504942122; _gat=1',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'
}


class Property:
    def __init__(self, url='', rules='re', selector='', headers=header, parser='lxml'):
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
            for match in soup.select(rules):
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
                for match in pattern.findall(html):
                    yield match

    def get_info(self):
        html = self.get_html()
        if self.selector.lower() == 'select':
            if html:
                print('use select selector')
                return self._select_info(html, self.rules)
        elif self.selector.lower() == 're':
            if html:
                print('use re selector')
                return self._re_info(html, self.rules)

        elif self.selector.lower() == 'mix':
            if html:
                return self._mixed_info(html, self.rules)
        else:
            print('Please specify specific parser!!')





"""
dd = soup.select('div.book-detail > dl > dd')
dt = soup.select('div.book-detail > dl > dt')

ddd = [ddd.text for ddd in dd]
ttt = [ttt.text for ttt in dt]

dsc = dict(zip(ttt, ddd))


"""

#所有书籍分类提取规则
categories_info_rules = 'ul.sub-menu > li > ul > li > a'

#该分类下所有书籍的概要信息提取规则
briefly_info_rules = r'<img.*?src="(.*?)".*?/>.*?<h2.*?<a href="(.*?)"\s*rel=.*?>(.*?)</a>.*?<h5 class="entry-author">.*?<a href="(.*?)".*?>(.*?)</a></h5>.*?<div\s*class="entry-summary".*?<p>(.*?)</p>'

#该分类名称(后面下载书籍时留作新建目录用以该分类作为文件夹名称)和该分类下所含书籍的总页数
total_page_rules = r'<h1.*?>(.*?)</h1>.*?title="Last Page &rarr;">(\d+)</a>'

#书籍的详细信息提取规则
detail_info_rules = r''



"""
 <div class="book-detail">
     <dl>
     <dt>Author:</dt><dd> <a href="http://www.allitebooks.com/author/lee-naylor/" rel="tag">Lee Naylor</a></dd>
     <dt>ISBN-10:</dt><dd> 1484221362</dd>
     <dt>Year:</dt><dd> 2016</dd>
     <dt>Pages:</dt><dd> 608</dd>
     <dt>Language:</dt><dd> English</dd>
     <dt>File size:</dt><dd> 30.6 MB</dd>
     <dt>File format:</dt><dd> PDF</dd>
     <dt>Category:</dt><dd> <a href="http://www.allitebooks.com/web-development/asp-net/" rel="category" >ASP.NET</a> <a href="http://www.allitebooks.com/web-development/html-html5-css/" rel="category" >HTML, HTML5 &amp; CSS</a></dd>
   </dl>   
  </div>

"""




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

'http://www.allitebooks.com/web-development/asp-net/page/2/'

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



#获取分类名称和总页数, 传入Property类实例
def getdicandpage(property):
    subpage = property
    catageinfo = subpage.get_info()
    for i in catageinfo:
        subpage.directory, subpage.total_page_numbers = i
    return subpage.directory.strip(), subpage.total_page_numbers.strip()

#产生该分类下每一页的链接
def generate_page_link(linkseed, start, end='', suffix=''):
    for link in [linkseed + suffix + '{}'.format(str(i)) for i in range(int(start), int(end) + 1)]:
        yield link

def main():
    mainentrance = 'http://www.allitebooks.com/'
    # suburl = 'http://www.allitebooks.com/web-development/asp-net/'
    # html = get_html(suburl)
    # # get_link(html, categories_rules)
    # for item in get_link(html, briefly_info_rules):
    #     print(item)
        #print(re.sub('^[\/:*?"<>.|]', 'File_', item[0]), item[1])

    mainpage = Property(mainentrance, categories_info_rules, 'select')

    # 分类目录链接循环
    for category in mainpage.get_info():

        # for item in get_single_link(itemlist):
        #     get_one_page_briefly(subpage, item.get('href'))
        #     return
        subpage = Property(category.get('href'), total_page_rules, 're')

        # 获取单个分类名称和总页数
        directory, total_page_numbers = getdicandpage(subpage)
        print(directory, total_page_numbers)

        # briefly_info_rules 单个分类下,所有书籍概要信息提取规则
        subpage.rules = briefly_info_rules

        # 单个分类下所有页索引循环
        for link in generate_page_link(subpage.url, 1, total_page_numbers, r'page/'):
            subpage.url = link
            print(subpage.url)

            # 单个分类下每一页书籍概要信息循环
            for info in subpage.get_info():
                print(info)
        return

if __name__ == '__main__':
    main()