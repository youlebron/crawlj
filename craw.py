# encoding:utf8

import urllib2
import jsonpickle


def req(url):
    req = urllib2.Request(url)
    json = urllib2.urlopen(req).read()
    return json

def handlereq(a):
    if a.has_key('data'):
        if a['data'].has_key('list'):
            # projs = reduce(lambda a, b: a + "," + b, [d['project_name'] for d in a['data']['list']])
            for projname in [d['project_name'] for d in a['data']['list']]:
                url = "https://nj.fang.lianjia.com/loupan/p_%s" % projname
                json = urllib2.urlopen(url).read()
                print ret

url = r'https://nj.fang.lianjia.com/loupan/bp200ep350nht1nht6nhs1/?_t=1'
a = jsonpickle.loads(req(url))
total = a['data']['total']
page = int(total / 10) + 1
handlereq(a)    # handle page 1
for i in range(2, page + 1):
    url = r'https://nj.fang.lianjia.com/loupan/bp200ep350nht1nht6nhs1pg%s/?_t=1' % i
    a = jsonpickle.loads(req(url))
    handlereq(a)


