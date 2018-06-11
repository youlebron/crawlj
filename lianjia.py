# -*- coding: utf-8 -*-
import urllib2

import jsonpickle
import scrapy
import requests
from lxml import etree
from ..items import LianjiaItem
from scrapy_redis.spiders import RedisSpider
from math import radians, cos, sin, asin, sqrt
import os

os.environ['http_proxy'] = 'http://127.0.0.1:3128'
os.environ['https_proxy'] = 'http://127.0.0.1:3128'

# regions = ['gulou','jianye','qinhuai','xuanwu','yuhuatai','qixia','jiangning','pukou']
regions = ['qixia','jiangning','pukou']


class LianjiaSpider(RedisSpider):
    start_page = 1
    name = 'lianjiaspider'
    redis_key = 'lianjiaspider:urls'

    def start_requests(self):
        for region in regions:
            start_urls = 'http://nj.lianjia.com/ershoufang/%s/pg%ssf1p4p5p6/' % (region, self.start_page)
            user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 \
                             Safari/537.36 SE 2.X MetaSr 1.0'
            headers = {'User-Agent': user_agent}
            yield scrapy.Request(url=start_urls, headers=headers, method='GET', callback=self.parse, meta={"region": region}, dont_filter=True)

    def parse(self, response):
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 \
                                 Safari/537.36 SE 2.X MetaSr 1.0'
        headers = {'User-Agent': user_agent}
        selector = etree.HTML(response.body.decode('utf-8'))
        houselist = selector.xpath('/html/body/div[4]/div[1]/ul/li')
        total_page = jsonpickle.loads(selector.xpath("/html/body//div[@class='page-box house-lst-page-box']/@page-data").pop())['totalPage']
        for house in houselist:
            try:
                item = LianjiaItem()
                item['title'] = house.xpath('div[1]/div[1]/a/text()').pop()
                item['community'] = house.xpath('div[1]/div[2]/div/a/text()').pop()
                item['model'] = house.xpath('div[1]/div[2]/div/text()').pop().split('|')[1]
                item['build_space'] = house.xpath('div[1]/div[2]/div/text()').pop().split('|')[2]
                item['focus_num'] = house.xpath('div[1]/div[4]/text()').pop().split('/')[0]
                item['watch_num'] = house.xpath('div[1]/div[4]/text()').pop().split('/')[1]
                item['price'] = house.xpath('div[1]/div[6]/div[1]/span/text()').pop()
                item['average_price'] = house.xpath('div[1]/div[6]/div[2]/span/text()').pop()
                item['link'] = house.xpath('div[1]/div[1]/a/@href').pop()

                item['decorate_type'] = house.xpath('div[1]/div[2]/div/text()').pop().split('|')[4]
                dt = house.xpath('div[1]/div[2]/div/text()').pop()
                item['have_flat'] = dt.split('|')[5] if len(dt.split('|')) >= 6 else u"无"
                # item['bizcircle_name'] = house.xpath('div[1]/div[3]/div/text()').pop().split('-')[1]
                self.url_detail = house.xpath('div[1]/div[1]/a/@href').pop()
                self.get_latitude(self.url_detail, item)
            except:
                print "数据错误1"
                continue
            yield item
        for i in range(self.start_page + 1, total_page + 1):
            url = 'http://nj.lianjia.com/ershoufang/%s/pg%ssf1p4p5p6/' % (response.meta.get("region"), i)
            contents = etree.HTML(requests.get(url).content.decode('utf-8'))
            houselist = contents.xpath('/html/body/div[4]/div[1]/ul/li')
            for house in houselist:
                try:
                    item = LianjiaItem()
                    item['title'] = house.xpath('div[1]/div[1]/a/text()').pop()
                    item['community'] = house.xpath('div[1]/div[2]/div/a/text()').pop()
                    item['model'] = house.xpath('div[1]/div[2]/div/text()').pop().split('|')[1]
                    item['build_space'] = house.xpath('div[1]/div[2]/div/text()').pop().split('|')[2]
                    item['focus_num'] = house.xpath('div[1]/div[4]/text()').pop().split('/')[0]
                    item['watch_num'] = house.xpath('div[1]/div[4]/text()').pop().split('/')[1]
                    item['price'] = house.xpath('div[1]/div[6]/div[1]/span/text()').pop()
                    item['average_price'] = house.xpath('div[1]/div[6]/div[2]/span/text()').pop()
                    item['link'] = house.xpath('div[1]/div[1]/a/@href').pop()

                    item['decorate_type'] = house.xpath('div[1]/div[2]/div/text()').pop().split('|')[4]
                    dt = house.xpath('div[1]/div[2]/div/text()').pop()
                    item['have_flat'] = dt.split('|')[5] if len(dt.split('|')) >= 6 else "无"
                    self.url_detail = house.xpath('div[1]/div[1]/a/@href').pop()
                    self.get_latitude(self.url_detail, item)
                except Exception, e:
                    continue
                yield item

    def get_latitude(self, url, item):  # 进入每个房源链接抓经纬度
        p = requests.get(url)
        contents = etree.HTML(p.content.decode('utf-8'))
        # time.sleep(1)
        latitude = contents.xpath('/html/body/script[21]/text()').pop()
        regex = '''resblockPosition(.+)'''
        items = re.search(regex, latitude)
        content = items.group()[:-1]  # 经纬度
        longitude_latitude = content.split(':')[1]
        item['latitude'] = longitude_latitude.split(",")[1].split("'")[0]
        item['longitude'] = longitude_latitude.split(",")[0].split("'")[1]
        baseinfo = contents.xpath('/ html / body // div[@id="introduction"]/div/div')[0]
        item['real_space'] = baseinfo.xpath("div[1]/div[2]/ul/li[5]/text()").pop()
        item['build_floor'] = baseinfo.xpath("div[1]/div[2]/ul/li[2]/text()").pop()
        item['check_sale_time'] = baseinfo.xpath("div[2]/div[2]/ul/li[1]/span[2]/text()").pop()
        item['last_sale_time'] = baseinfo.xpath("div[2]/div[2]/ul/li[3]/span[2]/text()").pop()
        item['build_year'] = baseinfo.xpath("div[2]/div[2]/ul/li[5]/span[2]/text()").pop()
        item['build_diya'] = baseinfo.xpath("div[2]/div[2]/ul/li[7]/span[2]/text()").pop()
        try:
            baseinfo = contents.xpath('/ html / body // div[@id="layout"]/div')[0]
            item['model_url'] = baseinfo.xpath(".//div[@class='imgdiv']/img/@src").pop()
        except:
            item['model_url'] = ""
        url = "http://api.map.baidu.com/direction/v2/transit?origin=%s,%s&destination=32.012825,118.780906&ak=B679df941bebfae64ebf9815ca3fa869" % (
            item['latitude'], item['longitude'])
        ret = jsonpickle.loads(urllib2.urlopen(url).read())
        if ret.has_key('status') and ret['status'] == 0:
            minlx = ret['result']['routes'][0]
            gjlx = [x[0]['instructions'] for x in minlx['steps']]
            zjdt = ""
            total_time = 0
            walk_time, car_time, train_time = 0, 0, 0
            find_zjdt = False
            for x in minlx['steps']:
                x = x[0]
                if u"乘地铁" in x['instructions']:
                    if not find_zjdt:
                        zjdt = x['instructions'].split(u"乘地铁")[0]
                        lon1, lat1, lon2, lat2 = map(radians, [float(item['longitude']), float(item['latitude']), float(x['start_location']['lng']),
                                                               float(x['start_location']['lat'])])
                        item['distance2train'] = 2 * asin(
                            sqrt(sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2)) * 6371 * 1000
                        find_zjdt = True
                    train_time += x['duration']
                elif u"步行" in x['instructions']:
                    walk_time += x['duration']
                else:
                    car_time += x['duration']
                total_time += int(x['duration'])
            item['distance'], item['minlx_distance'], item['routes'], item['train_station'], item['total_time'], item['walk_time'], item['car_time'], item[
                'train_time'] = ret['result']['taxi']['distance'], minlx['distance'], reduce(lambda a, b: a + " " + b,
                                                                                             gjlx), zjdt, total_time, walk_time, car_time, train_time
        else:
            item['distance'], item['minlx_distance'], item['routes'], item['train_station'], item['total_time'], item['walk_time'], item['car_time'], item[
                'train_time'] = 2 << 32, 2 << 32, "", "", 2 << 32, 2 << 32, 2 << 32, 2 << 32

# items.py

import scrapy
class LianjiaItem(scrapy.Item):
    # 标签  小区  户型   面积   关注人数  观看人数  发布时间  价格   均价  详情链接  经纬度 城区
    title = scrapy.Field()
    community = scrapy.Field()
    model = scrapy.Field()
    focus_num = scrapy.Field()
    watch_num = scrapy.Field()
    price = scrapy.Field()
    average_price = scrapy.Field()
    link = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    check_sale_time = scrapy.Field()
    last_sale_time = scrapy.Field()
    build_space = scrapy.Field()
    build_floor = scrapy.Field()
    real_space = scrapy.Field()
    build_year = scrapy.Field()
    build_diya = scrapy.Field()

    have_flat = scrapy.Field()
    decorate_type = scrapy.Field()
    bizcircle_name = scrapy.Field()

    model_url = scrapy.Field()
    model_intro = scrapy.Field()

    distance = scrapy.Field()
    minlx_distance = scrapy.Field()
    train_station = scrapy.Field()
    total_time = scrapy.Field()
    walk_time = scrapy.Field()
    car_time = scrapy.Field()
    train_time = scrapy.Field()
    routes = scrapy.Field()
    distance2train = scrapy.Field()

#pipelines
import jsonpickle
import pymongo
import redis
from scrapy.conf import settings

import constants
from .items import LianjiaItem

class LianjiaPipeline(object):
    def __init__(self):
        redis_conf = "10.171.125.56:6379:1".split(":")
        redis_pool = redis.ConnectionPool(host=redis_conf[0], port=redis_conf[1], db=redis_conf[2])
        r = redis.Redis(connection_pool=redis_pool)
        self.post = r

    def process_item(self, item, spider):
        if isinstance(item,LianjiaItem):
            try:
                info = dict(item)
                if self.post.lpush(constants.ITEM_STORE_KEY, info):
                    print('bingo')
            except Exception:
                pass
        return item


#settings
BOT_NAME = 'LianJia'

SPIDER_MODULES = ['LianJia.spiders']
NEWSPIDER_MODULE = 'LianJia.spiders'


ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 3

SCHEDULER = "scrapy_redis.scheduler.Scheduler"    #调度
REDIS_HOST = '10.171.125.56'
REDIS_PORT = 6379
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"  #去重
SCHEDULER_PERSIST = False       #不清理Redis队列
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderQueue"    #队列

ITEM_PIPELINES = {
   'LianJia.pipelines.LianjiaPipeline': 300,
}
