# encoding:utf8

import urllib2
import jsonpickle
import os

from BeautifulSoup import BeautifulSoup

os.environ['http_proxy'] = 'http://127.0.0.1:3128'
os.environ['https_proxy'] = 'http://127.0.0.1:3128'
newhlist = []


def req(url):
    req = urllib2.Request(url)
    json = urllib2.urlopen(req).read()
    return json

district_names = u"鼓楼 建邺 秦淮 玄武 雨花台 栖霞 江宁 浦口".split(" ")


def handlereq(a):
    if a.has_key('data'):
        if a['data'].has_key('list'):
            # projs = reduce(lambda a, b: a + "," + b, [d['project_name'] for d in a['data']['list']])
            for data in a['data']['list']:
                if data['district_name'] not in district_names:
                    continue
                if data['house_type'] != u"住宅":
                    continue
                projname = data['project_name']
                url = "https://nj.fang.lianjia.com/loupan/p_%s" % projname
                html = urllib2.urlopen(url).read()
                parsed_html = BeautifulSoup(html)
                text = parsed_html.body.find('div', attrs={'id': 'house-details'}).text.encode('utf8')
                company = text.split("物业公司：")[1].split("最新开盘")[0].decode("utf8")
                jfsj = text.split("交房时间：")[1].split("容积率")[0]
                try:
                    totalscore = parsed_html.body.find('span', attrs={'class': 'score'}).text.encode('utf8').split("分")[0]
                except:
                    totalscore = 3.11
                ndata = {"resblock_name": data['resblock_name'], "avg_price_start": data['avg_price_start'], "address_remark": data['address_remark'],
                         "min_frame_area": data['min_frame_area'], "max_frame_area": data['max_frame_area'], "show_price": data["show_price"],
                         "latitude": data["latitude"], "longitude": data["longitude"], "totalscore": "totalscore", "resblock_frame_area": data['resblock_frame_area'],
                         "open_date": data['open_date'], "jfsj": jfsj, "bizcircle_name": data['bizcircle_name'],
                         'process_status': data['process_status'], 'district_name': data['district_name'], 'company': company, 'jfsj': jfsj,
                         'totalscore': totalscore,'url':url}
                newhlist.append(ndata)

url = r'https://nj.fang.lianjia.com/loupan/bp200ep350nht1nht6nhs1/?_t=1'
a = jsonpickle.loads(req(url))
total = a['data']['total']
page = int(int(total) / 10) + 1
handlereq(a)  # handle page 1
for i in range(2, page + 1):
    url = r'https://nj.fang.lianjia.com/loupan/bp200ep350nht1nht6nhs1pg%s/?_t=1' % i
    a = jsonpickle.loads(req(url))
    handlereq(a)

import xlwt

style = xlwt.easyxf('font: name Consolas, bold on')
wb = xlwt.Workbook(encoding="utf-8")
wb.__dict__['_Workbook__sst'].encoding = 'utf-8'
ws = wb.add_sheet(u"新房")
rcnt = 1
cnt = 0
for k, v in dict(newhlist[0]).iteritems():
    ws.write(0, cnt, k, style)
    cnt += 1
for data in newhlist:
    cnt = 0
    for k, v in dict(data).iteritems():
        ws.col(cnt).width = 15 * 256
        v = v if type(v) == unicode else jsonpickle.encode(v)
        ws.write(rcnt, cnt, v, style)
        cnt += 1
    rcnt += 1
wb.save(os.path.join("./", u"新房.xls"))
