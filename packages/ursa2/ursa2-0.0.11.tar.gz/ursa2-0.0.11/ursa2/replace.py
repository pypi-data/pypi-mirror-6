#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
 replace.py

 changelog
 2013-12-01[11:42:20]:created

 @info yinyong,osx-x64,UTF-8,192.168.1.101,py,/Users/yinyong/work/ursa2/src
 @author yanni4night@gmail.com
 @version 0.0.1
 @since 0.0.1
'''

from conf import C,log
import re
import utils

range_item=0

def replace(content,target=None):
    '''
    替换@@变量
    '''
    TM_TOKEN = '@tm:(.+?)@'
    DATE_TOKEN = '@date@';
    COMMON_TOKEN = r'@([\w\-\/\\]+?)@'
    

    iters = re.finditer( TM_TOKEN , content )
    for i in reversed(list(iters)):
        file_path = i.group(1)
        if file_path.startswith('/'):
            file_path=file_path[1:]
        file_path=utils.abspath(file_path)
        content = content[0:i.start(0)] + utils.get_file_timestamp(file_path) + content[i.end(0):]

    iters = re.finditer( DATE_TOKEN , content )
    for i in reversed(list(iters)):
        content = content[0:i.start(0)] + utils.getDate()  + content[i.end(0):]

    iters = re.finditer( COMMON_TOKEN , content )

    for i in reversed(list(iters)):
        name = i.group(1)
        value = C(name,target)
        if value is not None:
            if utils.isStr(value) and value.find('{num}') != -1:
                num = int(C('num',target))
                num = range(num+1)
                substr100 = content[i.end(0):i.end(0)+100]#what
                istimestamp = substr100.find('%s='%C('timestamp_name'))
                if istimestamp != -1:#has timestamp
                    try:
                        tm = int(substr100[istimestamp+2:istimestamp+3])
                    except ValueError:
                        continue
                    if tm >= len(num):
                        tm = tm - len(num)
                    value = value.replace( '{num}' , str(tm) )
                else:
                    global range_item
                    value = value.replace( '{num}' , str(num[range_item]) )
                    range_item = range_item + 1
                    if range_item >= len(num):
                        range_item = 0
            content = content[0:i.start(0)] + str(value) + content[i.end(0):]
    return content