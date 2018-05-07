# -*- coding: utf-8 -*-
import urllib2

from BeautifulSoup import BeautifulSoup


import os
os.environ['http_proxy'] = 'http://127.0.0.1:3128'
os.environ['https_proxy'] = 'http://127.0.0.1:3128'
url = "https://nj.fang.lianjia.com/loupan/p_%s" % "hyyzsgcxablwc"
html = urllib2.urlopen(url).read()
parsed_html = BeautifulSoup(html)
text = parsed_html.body.find('div', attrs={'id':'house-details'}).text.encode('utf8')
company = text.split("物业公司：")[1].split("最新开盘")[0]
jfsj = text.split("交房时间：")[1].split("容积率")[0]
totalscore = parsed_html.body.find('span', attrs={'class':'score'}).text.encode('utf8').split("分")[0]
print totalscore,company,jfsj

'''
楼盘详情<ul class="clear tab">
      		<li class="tab-loupan">
            <span><i></i>楼盘信息</span>
          </li>
      		<li class="tab-wuye no-click">
            <span><i></i>物业信息</span>
          </li>
	    </ul>项目地址：梨树园路10号售楼处地址：梨树园路10号（接待时间 9:00 - 18:00）开发商：南京禹阳东房地产开发有限公司物业公司：南京弘阳物业管理有限公司最新开盘：2018-04-07物业类型：住宅交房时间：2019-11-30容积率：2.00产权年限：70年绿化率：31.21规划户数：693物业费用：1.9元/m²/月车位情况：地上车位数140
                                        ；                                            地下车位数598供暖方式：自采暖供水方式：民水供电方式：民电建筑类型：板楼嫌恶设施：暂无占地面积：32,246㎡建筑面积：87,258㎡查看更多
'''