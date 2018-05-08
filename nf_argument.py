# -*- coding: utf-8 -*-

'''
{
            "name":"中华门-地铁站",
            "location":{
                "lat":32.012825,
                "lng":118.780906
            },
            "address":"1号线;(规划)8号线",
            "province":"江苏省",
            "city":"南京市",
            "area":"秦淮区",
            "street_id":"48c9cda9bd5a4123adb22ab2",
            "detail":1,
            "uid":"48c9cda9bd5a4123adb22ab2"
        }
'''
import urllib2

import os

import jsonpickle

os.environ['http_proxy'] = 'http://127.0.0.1:3128'
os.environ['https_proxy'] = 'http://127.0.0.1:3128'

import pandas as pd

xfs = pd.read_excel(u"./新房.xls")


def lx(row):
    url = "http://api.map.baidu.com/direction/v2/transit?origin=%s,%s&destination=32.012825,118.780906&ak=B679df941bebfae64ebf9815ca3fa869" % (
    row['latitude'], row['longitude'])
    ret = jsonpickle.loads(urllib2.urlopen(url).read())
    if ret.has_key('status') and ret['status'] == 0:
        minlx = ret['result']['routes'][0]
        gjlx = [x[0]['instructions'] for x in minlx['steps']]
        zjdt = ""
        total_time = 0
        walk_time, car_time, train_time = 0, 0, 0
        for x in gjlx:
            if u"乘地铁" in x:
                zjdt = x.split(u"乘地铁")[0]
                break
        for x in minlx['steps']:
            x = x[0]
            if u"乘地铁" in x['instructions']:
                train_time += x['duration']
            elif u"步行" in x['instructions']:
                walk_time += x['duration']
            else:
                car_time += x['duration']
            total_time += int(x['duration'])
        return ret['result']['taxi']['distance'], minlx['distance'], reduce(lambda a,b:a+" "+b, gjlx), zjdt, total_time, walk_time, car_time, train_time
    return 2 << 32, 2 << 32, "", "", 2 << 32, 2 << 32, 2 << 32, 2 << 32


xfs['etotal'] = xfs.apply(lx, axis=1)
xfs['distance'] = xfs['etotal'].apply(lambda x:x[0])
xfs['minlx_distance'] = xfs['etotal'].apply(lambda x:x[1])
xfs['train_station'] = xfs['etotal'].apply(lambda x:x[3])
xfs['total_time'] = xfs['etotal'].apply(lambda x:x[4])
xfs['walk_time'] = xfs['etotal'].apply(lambda x:x[5])
xfs['car_time'] = xfs['etotal'].apply(lambda x:x[6])
xfs['train_time'] = xfs['etotal'].apply(lambda x:x[7])
xfs['routes'] = xfs['etotal'].apply(lambda x:x[2])
xfs = xfs.drop(columns = ['etotal'])
xfs.to_excel(u"./新房_argu.xls", encoding='utf-8')
