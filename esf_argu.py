# -*- coding: utf-8 -*-

import pandas as pd

import constants

df = pd.read_excel(constants.EXCEL_NAME)


def sdiff(row):
    diff = 0 if row['real_space'] == u"暂无数据" else float(row['build_space']) - float(row['real_space'])
    diff = 40 if diff > 40 else diff
    diff = 0 if diff < 0 else diff
    return diff
df['space_diff'] = df.apply(sdiff, axis=1)
import re
def bf(row):
    m = re.compile("[\\d]+").findall(row)
    v = m[0]
    if row[0] == u"低":
        v = 1
    elif row[0] == u"中":
        v = int(int(v)/2)
    return v
df['floor_num'] = df['build_floor'].apply(bf)

def fp(row):
    v = row['have_flat']
    if v == 1:
        return 10
    else:
        r = -1.2 * int(row['floor_num']) + 10
    return r if r > 0 else 0
df['flat_point'] = df.apply(fp,axis=1)
df['flat_point'].head()

import time
def datestr2stamp(str):
    str= str.replace('"',"",-1)
    try:
        st = time.strptime(str, "%Y-%m-%d")
    except:
        return int(time.time())
    return time.mktime(st)
def year2now(str):
    return (int(time.time()) - datestr2stamp(str))/(3600*24*365)
df['check_time'] = df['check_sale_time'].apply(lambda x:year2now(x))
df['scjy_time'] = df['last_sale_time'].apply(lambda x:year2now(x))

def yp(row):
    if row['build_year']==5:
        base_p = 10
    elif row['build_year']==2:
        base_p = 5
    else:
        return 0
    r = base_p
    if row['check_time'] > 0.15:
        r = -8 * (row['check_time']) + r
    if row['scjy_time'] > 10:
        r = -0.3 * (row['scjy_time']) + r
    return r if r > 0 else 0
df['year_point'] = df.apply(yp,axis=1)
df['year_point'].head()

def pp(row):
    v = row['price']
    v= float(v.replace('"',"",-1))
    r = 5
    if v > 320:
        r = -0.25 * (v-320) + r
    r2 = 5
    v = row['average_price']
    if v > 32000:
        r2 = -0.0025 * (v-32000) + r2
    r = r+r2
    return r if r > 0 else 0
df['price_point'] = df.apply(pp,axis=1)
df['price_point'].head()

max_fp = df['focus_num'].mean()
min_fp = df['focus_num'].min()
max_wn = df['watch_num'].mean()
min_wn = df['watch_num'].min()
def focp(row):
    a = 5 if row['focus_num']>max_fp else ((row['focus_num']-min_fp)/(max_fp-min_fp))*5
    b = 5 if row['watch_num']>max_wn else ((row['watch_num']-min_wn)/(max_wn-min_wn))*5
    return  a+b
df['focus_point'] = df.apply(focp, axis=1)
df['focus_point'].head()

def sp(v):
    if v > 0 and v < 13:
        return 10
    if v == 0:
        return 4
    r = -0.5 * (v-13) + 10
    return r if r > 0 else 0
df['space_point'] = df['space_diff'].apply(sp)
df['space_point'].head()

tt_mean = df['total_time'].mean()
wt_mean = df['walk_time'].mean()
def roup(row):
    if row['train_station'].strip() != '""':
        r = 20
        if row['total_time']>tt_mean:
            r = -0.01 * (row['total_time']-tt_mean) + r
        elif row['total_time']<0.8*tt_mean:
            r = -0.01 * (row['total_time']-0.8*tt_mean) + r
        if row['walk_time']>wt_mean:
            r = -0.02 * (row['walk_time']-wt_mean) + r
        elif row['walk_time']<0.8*wt_mean:
            r = -0.01 * (row['walk_time']-wt_mean) + r
        if row['car_time']>1200:
            r = -0.03 * (row['car_time']) + r
        elif row['car_time']>300:
            r = -0.025 * (row['car_time']) + r
        elif row['car_time']>0:
            r = -0.02 * (row['car_time']) + r
    else:
        r = 8
        if row['total_time']>0.3*tt_mean:
            r = -0.03 * (row['total_time']-0.3*tt_mean) + r
        if row['walk_time']>0.8*wt_mean:
            r = -0.02 * (row['walk_time']-0.8*wt_mean) + r
    return r
df['routes_point'] = df.apply(roup,axis=1)

df['decorate_point']=df['decorate_type'].apply(lambda x:1 if x.strip()==u"精装" else 0)

def real_spacep(row):
    space = float(row['build_space']) if row['real_space'] == u"暂无数据" else float(row['real_space'])
    r = 10
    if space < 80:
        r = -0.35 * (80-space) + r
    return r if r > 0 else 0
df['space_point2'] = df.apply(real_spacep,axis=1)

def totalp(r):
    r = r['routes_point']+r['flat_point']+r['space_point']+r['focus_point']+r['price_point']+r['year_point']+r['decorate_point']+r['space_point2']
    return r
df['total_point'] = df.apply(totalp,axis=1)
df = df.drop(columns=['check_time','scjy_time','title'])
df = df.sort_values(['total_point'], ascending=False)
df.to_excel(constants.SCORE_EXCEL_NAME, encoding='utf-8')

