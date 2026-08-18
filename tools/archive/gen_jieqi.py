# -*- coding: utf-8 -*-
"""生成节气表 jieqi.json，并校验前端排盘算法与 lunar-python 一致性。"""
import json, datetime
from lunar_python import Solar

GAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
ZHI = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

# 12 节 -> 月支索引 (八字月令以"节"为界)
JIE2ZHI = {'立春':2,'惊蛰':3,'清明':4,'立夏':5,'芒种':6,'小暑':7,
           '立秋':8,'白露':9,'寒露':10,'立冬':11,'大雪':0,'小寒':1}
ORDER = ['立春','惊蛰','清明','立夏','芒种','小暑','立秋','白露','寒露','立冬','大雪','小寒']

def gen_jieqi(start=1895, end=2100):
    data = {}
    for y in range(start, end+1):
        t = Solar.fromYmd(y, 1, 1).getLunar().getJieQiTable()
        arr = []
        for name in ORDER:
            jq = t[name]
            s = jq.toYmdHms()              # "YYYY-MM-DD HH:MM:SS"
            dp, tp = s.split(' ')
            mm, dd = dp.split('-')[1:3]
            hh, mn = tp.split(':')[0:2]
            arr.append("%02d-%02d %s:%s" % (int(mm), int(dd), hh, mn))
        data[str(y)] = arr
    return {'range':[start, end], 'order':ORDER, 'data':data}

# ---------- 前端算法复刻（用于校验） ----------
def day_gz(y, m, d):
    base = datetime.date(1900, 1, 1)
    diff = (datetime.date(y, m, d) - base).days
    base_idx = 10                        # 1900-01-01 = 甲戌
    return GAN[(base_idx%10 + diff) % 10] + ZHI[(base_idx%12 + diff) % 12]

def parse_item(item):
    dp, tp = item.split(' ')
    mm, dd = map(int, dp.split('-'))
    hh, mn = map(int, tp.split(':'))
    return mm, dd, hh, mn

def year_gz(y, m, d, hh, mm, jq):
    lm, ld, lh, lmn = parse_item(jq['data'][str(y)][0])  # 立春
    born = datetime.datetime(y, m, d, hh, mm)
    lichun = datetime.datetime(y, lm, ld, lh, lmn)
    yy = y if born >= lichun else y - 1
    idx = (yy - 4) % 60
    return GAN[idx % 10] + ZHI[idx % 12]

def month_gz(y, m, d, hh, mm, year_gan, jq):
    born = datetime.datetime(y, m, d, hh, mm)
    cands = []
    for yy in (y-1, y):
        arr = jq['data'][str(yy)]
        for i, name in enumerate(ORDER):
            mo, dd, h2, m2 = parse_item(arr[i])
            cands.append((datetime.datetime(yy, mo, dd, h2, m2), JIE2ZHI[name]))
    cands.sort(key=lambda x: x[0])
    zhi = 2
    for dt, z in cands:
        if born >= dt:
            zhi = z
    wuhu = {'甲':'丙','己':'丙','乙':'戊','庚':'戊','丙':'庚','辛':'庚',
            '丁':'壬','壬':'壬','戊':'甲','癸':'甲'}
    si = GAN.index(wuhu[year_gan])
    offset = (zhi - 2) % 12
    return GAN[(si + offset) % 10] + ZHI[zhi]

def hour_gz(day_gan, hh):
    if hh >= 23:
        zhi = 0; dg = GAN[(GAN.index(day_gan) + 1) % 10]   # 晚子时按次日日干
    else:
        zhi = (hh + 1) // 2 % 12
        dg = day_gan
    wushu = {'甲':'甲','己':'甲','乙':'丙','庚':'丙','丙':'戊','辛':'戊',
             '丁':'庚','壬':'庚','戊':'壬','癸':'壬'}
    return GAN[(GAN.index(wushu[dg]) + zhi) % 10] + ZHI[zhi]

def front_bazi(y, m, d, hh, mm, jq):
    yg = year_gz(y, m, d, hh, mm, jq)
    mg = month_gz(y, m, d, hh, mm, yg[0], jq)
    dg = day_gz(y, m, d)
    hg = hour_gz(dg[0], hh)
    return yg, mg, dg, hg

# ---------- 校验 ----------
def lunar_bazi(y, m, d, hh, mm):
    l = Solar.fromYmdHms(y, m, d, hh, mm, 0).getLunar()
    return l.getYearInGanZhi(), l.getMonthInGanZhi(), l.getDayInGanZhi(), l.getTimeInGanZhi()

SAMPLES = [
    (1964,9,10,0,0),   # 马云生日
    (1900,1,1,0,0),    # xlsx: 己亥 丙子 甲戌
    (1984,2,2,0,0),    # 立春前 -> 癸亥年
    (1984,2,5,0,0),    # 立春后 -> 甲子年
    (2026,2,3,12,0),   # 立春前 丑月
    (2026,2,5,12,0),   # 立春后 寅月
    (2026,8,11,23,30), # 晚子时
    (2023,3,22,0,0),   # 闰二月
    (2000,1,1,0,0),
    (2020,2,4,4,2),    # 立春精确时刻
    (2010,6,6,12,0),   # 芒种附近 午月
    (1995,12,7,0,0),   # 大雪附近 子月
    (2024,1,6,0,0),    # 小寒附近 丑月
    (1976,2,4,0,0),
    (1990,5,15,10,0),
]

if __name__ == '__main__':
    jq = gen_jieqi()
    with open(r'E:\michael\workBuddy\bazi-project\ui\jieqi.json', 'w', encoding='utf-8') as f:
        json.dump(jq, f, ensure_ascii=False)
    print('jieqi.json written, years=%d, size~%dKB' % (
        len(jq['data']), len(json.dumps(jq, ensure_ascii=False))//1024))
    print('--- 校验 (前=本算法, 后=lunar) ---')
    fails = 0
    for s in SAMPLES:
        f = front_bazi(*s, jq)
        lb = lunar_bazi(*s)
        ok = f == lb
        if not ok:
            fails += 1
        print(('PASS' if ok else 'FAIL'), s, 'front=', f, 'lunar=', lb)
    print('RESULT: %d/%d PASS' % (len(SAMPLES)-fails, len(SAMPLES)))
