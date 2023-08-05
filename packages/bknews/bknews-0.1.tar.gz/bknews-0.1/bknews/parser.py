#!/usr/bin/env python
import re
from urllib.request import urlopen
import html.parser
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

parser = html.parser.HTMLParser()

class News():
    """
    Represent news (from SIS, DTDH and CTSV).
    """
    def __init__(self, title='', news_id='', url='', content='', date=''):
        self.title = title
        self.news_id = news_id
        self.url = url
        self.content = content
        self.date = date

def news_from_sis():
    base_news_url = 'http://sis.hust.edu.vn/NewsModule/?ID='
    data = urlopen('http://sis.hust.edu.vn').read().decode()
    results = re.findall(
        '<div class="dxncItemDate_SisTheme".*?>.*?([0-9]+\/[0-9]+\/[0-9]+).*?</div>.*?<a href="NewsModule\/\?ID=([0-9]+)".*?><font .*?>(.*?)</font></a>', 
        data, re.S)
    all_news = []
    for date, index, title in results:
        url = base_news_url + index
        content = _from_sis(url)
        all_news.append(News(
            title=parser.unescape(title), 
            news_id=index, 
            url=url,
            content=content,
            date=date)
        )
    return all_news

def _from_sis(url):
    data = urlopen(url).read().decode()
    soup = BeautifulSoup(data)
    result = soup.find(id="dvNewsItem")
    return result.decode()

def _from_ctsv(url):
    pass

def _from_dtdh(url):
    pass

if __name__ == '__main__':
    all_news = news_from_sis()
    for news in all_news:
        print(news.date, news.news_id, news.title, news.url)