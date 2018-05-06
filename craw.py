#encoding:utf8

import urllib2
import jsonpickle


url = r'https://nj.fang.lianjia.com/loupan/bp200ep350nht1nht6nhs1/?_t=1'
req = urllib2.Request(url)
json = urllib2.urlopen(req).read()
a = jsonpickle.loads(json)
if a.has_key('data'):
    if a['data'].has_key('list'):
        projs = reduce(lambda a,b:a+","+b, [d['project_name']for d in a['data']['list']])
        url = "https://nj.fang.lianjia.com/loupan/agent/board/?city_id=320100&project_names="+projs
        json = urllib2.urlopen(url).read()
        print json


