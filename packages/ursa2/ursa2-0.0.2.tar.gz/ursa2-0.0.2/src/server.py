#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
 server.py

 changelog
 2013-11-30[17:37:42]:created
 2013-12-11[10:22:12]：https supported

 @info yinyong,osx-x64,UTF-8,192.168.1.101,py,/Users/yinyong/work/ursa2/src
 @author yinyong@sogou-inc.com
 @version 0.0.2
 @since 0.0.1
 @todo https support,proxy support
'''

from  BaseHTTPServer import HTTPServer,BaseHTTPRequestHandler
from http import Request,Response
from route import Route
from conf import C,log,BASE_DIR
import utils
import ssl
import os
import socket
from OpenSSL import SSL
from SocketServer import BaseServer
from handler import static,index,tpl,so,m,data

ursa_router=Route()
ursa_router.get(r'^/$',index)
ursa_router.get(r'\.%s$'%C('preview_ext'),tpl)
ursa_router.post(r'\.so$',so)
ursa_router.get(r'\.m$',m)
ursa_router.get(r'\.data$',data)
ursa_router.get(r'^/.+',static)

class UrsaHTTPRequestHandler(BaseHTTPRequestHandler):
    '''
    HTTP请求处理器
    '''

    def do_GET(self):
        '''
        处理GET请求
        '''
        ursa_router.distribute_request(self)

    def do_POST(self):
        '''
        todo:处理POST请求
        '''
        ursa_router.distribute_request(self)

    @classmethod
    def version_string(self):
        '''
        服务器名字
        '''
        return 'Ursa2'

    @classmethod
    def log_date_time_string(self):
        '''
        服务器日志日期格式
        '''
        return utils.getDate(fmt="%Y/%m/%d %H:%M:%S")
    
    def log_request(self , code , message=''):
        '''
        服务器日志输出
        '''
        if C('log_http_request'):
            return BaseHTTPRequestHandler.log_request(self,code,message)
        else:
            return ''
    def setup(self):
        '''
        for https
        '''
        self.connection = self.request
        self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
        self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)


class SecureHTTPServer(HTTPServer):
    '''
    HTTPS服务器，来自互联网
    '''
    def __init__(self, server_address, HandlerClass):
        BaseServer.__init__(self, server_address, HandlerClass)
        ctx = SSL.Context(SSL.SSLv23_METHOD)

        ctx.use_privatekey_file( os.path.join(BASE_DIR,"../assets","privatekey.pem"))
        ctx.use_certificate_file( os.path.join(BASE_DIR,"../assets","certificate.pem"))

        self.socket = SSL.Connection(ctx, socket.socket(self.address_family, self.socket_type))

        self.server_bind()
        self.server_activate()

def get_local_ip():
    '''
    获取本机IP
    '''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('w3.org',80))
        return s.getsockname()[0]
    except Exception, e:
        return '127.0.0.1'
    finally:
       try:
            s.close()
       except Exception, e:
           e

def run(port=8000):
    '''
    服务器启动入口
    '''
    try:
        port=int(port)
    except Exception, e:
        try:
            port=int(C('server_port'))
        except Exception, e:
            port=8000
 
    server_addr=('',port);
    try:
        if 'https' == C('protocol'):
            httpd=SecureHTTPServer(server_addr,UrsaHTTPRequestHandler)
            protocol = 'https'
        else:
            httpd=HTTPServer(server_addr,UrsaHTTPRequestHandler)
            protocol = 'http'
            
        print "Server listen on %s://%s:%d/" % (protocol,get_local_ip(), port)
        httpd.serve_forever()
    except (KeyboardInterrupt , SystemExit):
        print "Shutting down.Goodbye!"
        httpd.socket.close()
    except socket.error,e:
        log.error(e)
        sys.exit(1)

if __name__ == '__main__':
    run()