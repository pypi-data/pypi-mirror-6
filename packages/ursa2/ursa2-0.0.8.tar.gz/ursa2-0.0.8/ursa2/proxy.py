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
import mimetypes
import utils
import re
from conf import C,log

mimetypes.init()

def proxy(target_url,req,res):
    '''
    '''
    if not target_url:
        return res.send(code = 500,content = 'Empty url not supported')

    #二进制资源直接重定向
    parsed_url = urlparse(target_url)
    mime = mimetypes.guess_type(parsed_url.path,False)
    content_type = mime[0] or 'text/plain'
    if re.match( utils.BINARY_CONTENT_TYPE_KEYWORDS , content_type,re.IGNORECASE ):
        return res.redirect(target_url)

    if 'GET' == req.method:
        request = R.get
    elif 'POST' == req.method:
        request = R.post

    try:
        #通知远端服务器不要压缩
        if req.headers.get('accept-encoding'):
            del req.headers['accept-encoding']
        r = request(target_url,headers=req.headers)
        #本地服务器覆写Date和Server
        if r.headers.get('date'):
            del r.headers['date']
        if r.headers.get('server'):
            del r.headers['server']
        return res.send(code = r.status_code,content = r.content or '',headers =  r.headers)
    except Exception, e:
        log.error('[proxy]%s'%e)
        return res.send(code = 500,content = str(e))

def main():
    r = R.get('http://www.w3.org/TR/css3-color/',data={'name':"yes"})
    print r.headers.get('Content-Type')


if __name__ == '__main__':
    main()