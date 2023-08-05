#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
 proxy.py

 changelog
 2013-12-11[17:23:52]:created

 @info yinyong,osx-x64,Undefined,10.129.164.77,py,/Volumes/yinyong/ursa2/src
 @author yanni4night@gmail.com
 @version 0.0.1
 @since 0.0.1
'''

import requests as R
from urlparse import urlparse
import utils
import re
from conf import C,log


def get_proxy_url(req_path,reg,target):
    '''
    '''
    if not utils.isStr(reg) or not utils.isStr(target):
        log.warn('%s:%s is an illegal proxy pair'%(reg,target))
        return None
    if reg.startswith('regex:'):
        #正则匹配
        reg = reg[6:]
        if re.match(r'%s'%reg,req_path):
            target_path = re.sub(r'%s'%reg,r'%s'%target,req_path)
            return target_path
    elif reg.startswith('exact:'):
        #精确匹配
        reg = reg[6:]
        if reg == req_path:
            target_path = target
            return target_path
    else :
        #变量输出
        s = re.search('\$\{(.+)\}' , target)
        target_path= target
        if s:
            name = s.group(1)
            pattern = re.sub( '\{.+\}' , '(.+)' , reg )
            m = re.match(pattern, req_path )
            if m:
                path = m.group(1)
                target_path = target_path.replace( '${'+name+'}' , path )
                return target_path
    return None

def proxy(target_url,req,res):
    '''
    '''
    if not target_url:
        return res.send(code = 500,content = 'Empty url not supported')

    #二进制资源直接重定向
    parsed_url = urlparse(target_url)
    
    if utils.isBinary(parsed_url.path,strict = True):
        return res.redirect(target_url)

    if 'GET' == req.method:
        request = R.get
    elif 'POST' == req.method:
        request = R.post

    try:
        #通知远端服务器不要压缩
        if req.headers.get('accept-encoding'):
            del req.headers['accept-encoding']
        if req.headers.get('host'):
            del req.headers['host']
        log.info('[proxy]requesting %s'%target_url)

        r = request(target_url,headers = req.headers)
        #本地服务器覆写Date和Server
        if r.headers.get('date'):
            del r.headers['date']
        if r.headers.get('server'):
            del r.headers['server']
        if r.headers.get('transfer-encoding'):
            del r.headers['transfer-encoding']

        log.info('[proxy] status=%d'%r.status_code)

        return res.send(code = r.status_code,content = r.content or '',headers =  r.headers)
    except Exception, e:
        log.error('[proxy]%s'%e)
        return res.send(code = 500,content = '%s'%e)

def __test_content_type(url = False):
    r = R.get(url or 'http://www.sogou.com/web?query=k',headers={})
    print r.content#.get('Content-Type')

def __test_get_proxy_url():
    #print get_proxy_url('/search/xxx/1','regex:/search/(.+?)/(\d)','if you see this (\\1)(\\2)')
    #print get_proxy_url('/search/xxx/2','exact:/search/xxx/2','if you see this')
    print get_proxy_url('/search/xxx/3/2','/search/xxx/{m/d}','if you see this (${m/d})')

if __name__ == '__main__':
    __test_content_type()
    __test_content_type('http://www.baidu.com')