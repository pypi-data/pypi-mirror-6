#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
 http.py

 changelog
 2013-11-30[18:59:59]:created

 @info yinyong,osx-x64,UTF-8,192.168.1.101,py,/Users/yinyong/work/ursa2/src
 @author yinyong@sogou-inc.com
 @version 0.0.1
 @since 0.0.1
'''
from urlparse import urlparse,parse_qs
from conf import log,C
import utils
import re

class Request(object):
    '''
    HTTP请求
    '''

    @classmethod
    def __init__(self,http_req_handler):
        '''
        构造Request对象，
        拷贝HTTPRequestHandler的相关值
        '''
        self.path=urlparse(http_req_handler.path).path
        self.method=http_req_handler.command
        self.client_port=http_req_handler.client_address[1]
        self.client_host=http_req_handler.client_address[0]
        self.headers=http_req_handler.headers

        if 'GET' == self.method:
            #get请求解析url
            o=urlparse(http_req_handler.path)
            q=parse_qs(o.query)
            self.body=q
        elif 'POST' == self.method:
            #todo,post复杂解析
            content_len=int(http_req_handler.headers.get('Content-Length'))
            content=http_req_handler.rfile.read(content_len)
            q=parse_qs(content)
            self.body=q

    @classmethod
    def param(self,key):
        '''
        获取参数
        '''
        o=self.body.get(key)
        if o is None:
            return None

        if len(o) == 1:
            return o[0]
        else:
            return o

class Response(object):
    '''
    HTTP响应
    '''

    @classmethod
    def __init__(self,http_req_handler):
        '''
        '''
        self.http_req_handler=http_req_handler

    @classmethod
    def redirect(self,location,code=302):
        '''
        302重定向
        '''
        self.http_req_handler.send_response(302)
        self.http_req_handler.send_header('Location',location)
        self.http_req_handler.end_headers()
        self.http_req_handler.wfile.close()

    @classmethod
    def send(self,content=None,content_len=None,code=200,headers={}):
        '''
        '''
        self.http_req_handler.send_response(code)

        for k in headers.keys():
            self.http_req_handler.send_header(k,headers.get(k))
        if not headers.get('Content-Type'):
            headers['Content-Type']='text/html;charset='+C('encoding')

        if content is not None and not re.match(r'(image|video|flash|audio|powerpoint|msword)',headers['Content-Type'],re.IGNORECASE):
            try:
                content=content.encode(C('encoding'))
            except Exception, e:
                log.error('[send]%s'%(e))

        #填充Content-Length头
        if headers.get('Content-Length') is None and content_len is None and content is not None:
            content_len=len(content)
            if content_len > 0:
                self.http_req_handler.send_header('Content-Length',content_len)

        self.http_req_handler.end_headers()

        if content is not None:
                self.http_req_handler.wfile.write(content)

        self.http_req_handler.wfile.close()