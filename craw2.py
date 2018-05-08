# -*- coding: utf-8 -*-
import urllib2

import jsonpickle
from BeautifulSoup import BeautifulSoup


import os
os.environ['http_proxy'] = 'http://127.0.0.1:3128'
os.environ['https_proxy'] = 'http://127.0.0.1:3128'
# url = "https://nj.fang.lianjia.com/loupan/p_%s" % "hyyzsgcxablwc"
# html = urllib2.urlopen(url).read()
# parsed_html = BeautifulSoup(html)
# text = parsed_html.body.find('div', attrs={'id':'house-details'}).text.encode('utf8')
# company = text.split("物业公司：")[1].split("最新开盘")[0]
# jfsj = text.split("交房时间：")[1].split("容积率")[0]
# totalscore = parsed_html.body.find('span', attrs={'class':'score'}).text.encode('utf8').split("分")[0]
# print totalscore,company,jfsj

url = "http://api.map.baidu.com/direction/v2/transit?origin=%s,%s&destination=32.012825,118.780906&ak=B679df941bebfae64ebf9815ca3fa869" % (31.933852,118.945684)
print urllib2.urlopen(url).read()
