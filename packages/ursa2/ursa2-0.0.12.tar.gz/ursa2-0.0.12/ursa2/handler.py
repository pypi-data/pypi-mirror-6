#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
 handler.py

 changelog
 2013-11-30[22:32:36]:created
 2013-12-11[10:51:16]:better error report
 2013-12-16[17:16:32]:category of tpls
 2013-12-25[15:17:46]:s function supported,showing static resource

 @info yinyong,osx-x64,UTF-8,192.168.1.101,py,/Users/yinyong/work/ursa2/src
 @author yanni4night@gmail.com
 @version 0.0.2
 @since 0.0.1
'''
import utils
import mimetypes
from urlparse import urlparse
import os
import sys
import subprocess
import re
import json
from conf import C,log,BASE_DIR
from render import TokenRender,render_file
from replace import replace
from timestamp import html_link,html_script,html_img,all_url
from jinja2 import TemplateNotFound,TemplateSyntaxError
import requests as R

def _token(path):
    '''
    去除后缀，取得相对于模板目录的相对无扩展名路径
    '''
    tpl_token = re.sub(r'\.(%s|%s|%s|%s)$'%(C('preview_ext'),'m','data',C('template_ext')),'',path)
    tpl_token = utils.filterRelPath(tpl_token)
    return tpl_token


def index(req,res):
    '''
    模板列表
    '''
    tpl_dir = C('template_dir')
    tpl_ext = C('template_ext')
    tpls = utils.FileSearcher(r'\.%s$'%tpl_ext,tpl_dir).search()
    _tpls = []
    _module_tpls = []
    _common_tpls = []

    for e in tpls:
        e = re.sub(r'\.%s'%tpl_ext,'',e)
        if C('ignore_parents') and e.endswith('parent'):
            continue
        #分类输出
        if e.startswith(C('module_dir') + '/'):
            _module_tpls.append(e)
        elif e.startswith(C('common_dir') + '/'):
            _common_tpls.append(e)
        else:
            _tpls.append(e);

    index_path ='index.html'
    html = render_file(index_path,{"tpls":_tpls,"module_tpls":_module_tpls,"common_tpls":_common_tpls},noEnvironment = True)
    res.send(html)

def help(req,res):
    '''
    加载帮助文件
    '''
    inner_path = 'help.html'
    r = R.get('https://raw.github.com/yanni4night/ursa2/master/README.md')
    html = render_file(inner_path,{'content':r.content},noEnvironment = True)
    res.send(html)

def rs(req,res):
    '''
    静态资源列表
    '''
    static_dir = C('static_dir')
    img_dir = os.path.join(static_dir,C('img_dir'))
    js_dir = os.path.join(static_dir,C('js_dir'))
    css_dir = os.path.join(static_dir,C('css_dir'))

    imgs = utils.FileSearcher(r'\.(png|bmp|gif|jpe?g|ico)$',img_dir).search()
    csses =  utils.FileSearcher(r'\.(css|less)$',css_dir).search()
    jses =  utils.FileSearcher(r'\.js$',js_dir).search()

    static_path = 'static.html'#os.path.join(BASE_DIR,'tpl','static.html')
    html = render_file(static_path,{"img":imgs,"css":csses,"js":jses,"img_dir":img_dir,"css_dir":css_dir,"js_dir":js_dir},noEnvironment = True)
    res.send(html)


def tpl(req,res):
    '''
    模板
    '''
    tpl_token = _token(req.path)
    try:
        tr =TokenRender(tpl_token)
        return res.send(tr.render())
    except TemplateNotFound as e:
        return res.send(code = 500,content = 'Template %s not found' % (str(e) ,))
    except TemplateSyntaxError as e:
        return res.send(code = 500,content = 'Template %s:%d Syntax Error:%s' % (e.filename,e.lineno,e.message))
    except Exception, e:
        return res.send(code = 500,content = '%s'%e)

def data(req,res):
    '''
    获取对应模板的依赖数据组合
    '''
    tpl_token = _token(req.path)
    tr = TokenRender(tpl_token)
    data = tr.getData()
    return res.send(json.dumps(data),headers = {'Content-Type':'application/json'})

def m(req,res):
    '''
    输出对应json数据
    '''
    tpl_token = _token(req.path)
    data = ''
    json_path = os.path.join(C('data_dir'),tpl_token+".json")
    try:
        data = utils.readfile(json_path)
    except Exception, e:
        log.error('[m]%s:%s'%(json_path,e))
    mgr_path = 'mgr.html'# os.path.join(BASE_DIR,'tpl','mgr.html')
    html = render_file(mgr_path,{"name":tpl_token,"data":data},noEnvironment = True)
    res.send(html)

def so(req,res):
    '''
    保存json数据
    todo
    '''
    tpl_token = _token(req.param('tpl'))
    json_str = req.param('data')
    try:
        json_obj = json.loads(json_str)
        json_path = os.path.join(C('data_dir'),tpl_token+".json")
        utils.writeJSON(json_path,json_obj)
        res.redirect('/%s.%s'%(tpl_token,C('preview_ext')))
    except ValueError, e:
        res.send(render_file('json.html',{'json' : json_str,'tpl_token' : tpl_token} , noEnvironment = True))
    except Exception,e:
        log.error('[so]%s'%e)
        res.redirect('/%s.%s'%(tpl_token,C('preview_ext')))
    

def static(req,res):
    '''
    static resource
    '''
    req.path = utils.filterRelPath(req.path)
    o = urlparse(req.path)
    #取得绝对路径
    fd = utils.abspath(o.path)
    if fd.endswith('.css'):
        less = re.sub(r"\.css",".less",fd)
        if os.path.exists(less) and os.path.isfile(less):
            try:
                subprocess.call('lessc %s %s'%(less,fd),shell=True)
            except Exception, e:
                log.error('[less]%s'%e)
            
    if os.path.isfile(fd):
        mime = mimetypes.guess_type(fd,False)
        content_type = mime[0] or 'text/plain'#default text
        try:
            headers = {}
            #todo  custom defined
            if not utils.isBinary(fd):
                content = utils.readfile(fd)
                content = replace(content)
               
                if C('server_add_timestamp') :
                    if content_type.find('css') >= 0:
                        base_dir = os.path.dirname(fd)
                        content = all_url(content,base_dir)
                    elif content_type.find('html') >= 0:
                        content = html_link(content)
                        content = html_script(content)
                        content = html_img(content)
                        content = all_url(content)
                #http encoding header
                headers['Content-Encoding'] = C('encoding')
                headers['Cache-Control'] = 'nocache'
            else:
                #binary files
                content = utils.readfile(fd,'rb')

            headers['Content-Type'] = content_type
            res.send(content = content,headers = headers)
        except Exception, e:
            res.send(code = 500,content = '%s'%e)
            log.error("[static]%s"%e)
    else:
        if os.path.exists(fd):
            res.send(code = 403,content = 'Access %s is forbidden'%req.path)
        else:
            res.send(code = 404,content = "%s not found"%req.path)