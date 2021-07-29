# !/usr/bin/python3
# -*- coding: utf-8 -*-

# json 文本文件转化成csv

import csv

# json数据
import json
with open('json.txt', 'r', encoding='UTF-8') as f:
    rows = json.loads(f.read().encode().decode('utf-8-sig'), encoding='UTF-8')
# 创建文件对象
f = open('data.csv', 'w', encoding='utf-8-sig')
# 通过文件创建csv对象
csv_write = csv.writer(f)
# writerow: 按行写入，　writerows: 是批量写入
# 写入数据 取列表的第一行字典，用字典的ｋｅｙ值做为头行数据
csv_write.writerow(rows[0].keys())
# 循环里面的字典，将value作为数据写入进去
for row in rows:
    csv_write.writerow(row.values())
# 关闭打开的文件
f.close()
