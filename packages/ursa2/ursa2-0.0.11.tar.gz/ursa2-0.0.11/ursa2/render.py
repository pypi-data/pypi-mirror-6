#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
 render.py

 changelog
 2013-12-01[00:32:46]:created
 2013-12-14[23:52:33]:define TokenRender
 2013-12-17[12:13:55]:move removeCssDepsDeclaration out of class

 @info yinyong,osx-x64,UTF-8,192.168.1.101,py,/Users/yinyong/work/ursa2/src
 @author yanni4night@gmail.com
 @version 0.0.1
 @since 0.0.1
'''
from conf import C,log,BASE_DIR
import utils
import os
import re
import json
from timestamp import html_link,html_script,html_img,all_url,all as allt
from deps import DepsFinder
from replace import replace
from jinja2 import Template,Environment,FileSystemLoader,TemplateNotFound,TemplateSyntaxError

_template_dir = C('template_dir')

jinjaenv = Environment(loader = FileSystemLoader(utils.abspath(_template_dir),  C('encoding') ), extensions = ["jinja2.ext.do"] , autoescape = True )
build_jinjaenv = Environment( loader = FileSystemLoader( os.path.join( os.getcwd() , C('build_dir'), _template_dir) ,  C('encoding') ))
mgr_jinjaenv = Environment( loader = FileSystemLoader( os.path.join(BASE_DIR,'tpl') ,  C('encoding') ))

def render_file(filename,data = None,noEnvironment = False,build = False):
    '''
    渲染文件
    '''
    if noEnvironment:
        body = mgr_jinjaenv.get_template(filename)#Template(utils.readfile(filename))#这里应为绝对路径
    else:
        if build:
            body = build_jinjaenv.get_template(filename)
        else:
            body = jinjaenv.get_template(filename)
    return body.render(data or {})

def removeCssDepsDeclaration(html):
    '''
    移除HTML中对CSS的依赖声明
    '''
    return re.sub(r'<!\-\-[\s\S]*?@require[\s\S]*?\-\->','',html)

class TokenRender(object):
    '''
    '''
    @classmethod
    def __init__(self,token):
        self.__token = utils.filterPath(token)

        df = DepsFinder(token)
        self.__deps = df.find()
        self.__include_deps = df.findIncludes()
        self.__html = None

    @classmethod
    def getData(self,including_deps = True):
        data = {}
        if C('disable_deps_search') or not including_deps:
            deps = [self.__token+'.'+C('template_ext')]
        else:
            #复制
            deps = self.__deps[0:]
            deps.reverse()
        deps.insert(len(deps),self.__token+".json")
        deps.insert(0,"_ursa.json")
        for dep in deps:
            try:
                json_filepath = utils.abspath(os.path.join(C('data_dir'),re.sub(r'\.%s$'%C('template_ext'),'.json',dep)))
                content = utils.readfile(json_filepath)
                content = re.sub('\/\*[\s\S]*?\*\/','',content)
                json_data = json.loads(content)
                data.update(json_data)
            except Exception, e:
                e#log.warn('[getdata]%s:%s'%(json_filepath,e))
        return data

    @classmethod
    def render(self,build = False):
        '''
        查找数据文件依赖并渲染模板
        '''
        #remove '/'s at start
        if self.__html is None:
            data = self.getData()
            multoken = self.__token.split('/')
            data.update({'_token': self.__token.replace('/','_')})
            data.update({'_folder':multoken[0]})
            data.update({'_subtoken':multoken[1] if len(multoken)>1 else ""})
            tpl_path = self.__token + "." + C('template_ext')
            html = render_file( tpl_path,data,False,build)
            if C('server_add_timestamp'):
                #html = html_script(html)
                #html = html_link(html)
                #html = html_img(html)
                #html = all_url(html)
                html = allt(html)
            html = replace(html)
            if not build and not re.match(r'[\s\S]*?<html[\s\S]+?<body',html,re.I):
                #sub template
                css_deps = self.__getDepsCss(html)

                for tpl in self.__include_deps:
                    css = os.path.join('.',C('static_dir'),C('css_dir'),re.sub(r"\.%s"%C('template_ext'),".css",tpl))
                    css_deps.append(css)
                subparent = 'subparent.tpl'# os.path.join(BASE_DIR,"tpl",'subparent.tpl')
                html = render_file(subparent,{'name': self.__token,'content': html,'required_css': css_deps},noEnvironment = True)

            html = removeCssDepsDeclaration(html)
            self.__html = html
        return self.__html

    @classmethod
    def __getDepsCss(self,html):
        '''
        分析@require xxx.css,获取依赖
        '''
        ret = []
        iters = re.finditer(r'@require\s+?([/\w\-]+?\.css)',html,re.I)
        for it in reversed(list(iters)):
            css = it.group(1)
            css = utils.filterRelPath(css)
            ret.append( os.path.join('.',C('static_dir'),C('css_dir'),css) )
        return {}.fromkeys(ret).keys() 

if __name__ == '__main__':
    tr = TokenRender('index')
    print tr.render()
