#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
 build.py

 changelog
 2013-12-07[12:01:09]:created
 2013-12-10[22:40:30]:add build time show
 2013-12-15[01:04:04]:less supported

 @info yinyong,osx-x64,UTF-8,192.168.1.104,py,/Users/yinyong/work/ursa2/src
 @author yanni4night@gmail.com
 @version 0.0.1
 @since 0.0.1
'''

from conf import C,log,BASE_DIR
import logging
import shutil
import os
import re
import sys
import subprocess
import mimetypes
import utils
import time
from render import TokenRender,removeCssDepsDeclaration
from exception import ConfigurationError,DirectoryError
from replace import replace
from timestamp import html_link,html_script,html_img,all_url

RJS_PATH = os.path.join(BASE_DIR,'../assets','r.js')
RPL_PATH = os.path.join(BASE_DIR,'../assets','rpl.js')

#custom defined yuicompressor
__ycpath = C('yuicompressor')
YC_PATH = None
if __ycpath and utils.isStr( __ycpath ):
    if not os.path.exists( __ycpath ):
        log.warn('%s does not exist'%__ycpath )
    elif not os.path.isfile( __ycpath ) or not __ycpath.endswith('.jar'):
        log.warn('%s is not valid yuicompressor file')
    else:
        YC_PATH = __ycpath

if not YC_PATH:
    YC_PATH = os.path.join(BASE_DIR,'../assets','yuicompressor-2.4.8.jar')

mimetypes.init();

class UrsaBuilder(object):
    '''
    build project:
    copy and handle static resources
    generate html with json data
    '''
    @classmethod
    def __init__(self,compress,html,target=None):
        '''
        预先计算一些基础路径
        '''
        log.setLevel(logging.DEBUG)
        self._compress=compress
        self._generate_html=html
        self._target=target
        self._tpl_dir=C('template_dir')
        self._build_dir=C('build_dir')
        self._static_dir=C('static_dir')
        self._js_dir=C('js_dir')
        self._css_dir=C('css_dir')
        self._compile_dir=C('compile_folder') or ''#copy and repalce

        #check dunplicated
        if os.path.relpath(self._build_dir,self._tpl_dir) == '.':
            raise ConfigurationError('template_dir and build_dir are dumplicated')
        elif os.path.relpath(self._build_dir,self._static_dir)=='.':
            raise ConfigurationError('template_dir and static_dir are dumplicated')
        elif self._compile_dir and os.path.relpath(self._compile_dir,self._static_dir) == '.':
            raise ConfigurationError('compile_dir and static_dir are dunplicated')
        elif self._compile_dir and os.path.relpath(self._compile_dir,self._build_dir) == '.':
            raise ConfigurationError('compile_dir and build_dir are dunplicated')
        elif self._compile_dir and os.path.relpath(self._compile_dir,self._tpl_dir) == '.':
            raise ConfigurationError('compile_dir and tpl_dir are dunplicated')

        self._build_static_dir=os.path.join(self._build_dir,self._static_dir)
        self._build_css_dir=os.path.join(self._build_static_dir,self._css_dir,C('css_folder') or '')
        self._build_js_dir=os.path.join(self._build_static_dir,self._js_dir,C('js_folder') or '')
        self._build_tpl_dir=os.path.join(self._build_dir,self._tpl_dir)
        
        if self._compile_dir:
            self._build_compile_dir=os.path.join(self._build_dir,self._compile_dir)

        self._build_html_dir=os.path.join(self._build_dir,C('html_dir'))

    @classmethod
    def build(self):
        '''
        do build
        '''
        tmbegin = time.time()
        self._check();
        log.info ('copying directories')
        self._dir();
        log.info('handling less...');
        self._less();
        log.info ('handling css...')
        self._css();
        log.info ('handling  javascript...')
        self._js();
        log.info ('handling template...')
        self._tpl();
        if self._generate_html:
            log.info ('handling html...')
            self._html();
        log.info ('Time cost %s s.' % (time.time()-tmbegin) )

    @classmethod
    def _check(self):
        '''
        检查是否具备一个ursa2工程必备的文件和目录
        '''
        require_dirs=[self._tpl_dir,self._static_dir];
        for d in require_dirs:
            if not os.path.exists(d):
                raise DirectoryError('Ursas project requires %s directory'%d)

    @classmethod
    def _dir(self):
        '''
        handle build dir
        '''
        shutil.rmtree(self._build_dir,True)
        os.mkdir(self._build_dir);
        shutil.copytree(self._static_dir,self._build_static_dir)
        shutil.copytree(self._tpl_dir,self._build_tpl_dir)

        if self._compile_dir:
            shutil.copytree(self._compile_dir,self._build_compile_dir)

    @classmethod
    def _less(self):
        '''
        handle less files to css

        '''
        all_less_files=utils.FileSearcher(r'\.less$',self._build_css_dir,relative=False).search()
        for less in all_less_files:
            subprocess.call('lessc %s %s'%(less,re.sub(r"\.less",".css",less)),shell=True)
            os.remove(less)

    @classmethod
    def _css(self):
        '''
        handle css

        r.js会对不同目录下CSS合并时的URL进行修正，因而对于@something@开头的路径会被认为是相对路径，
        产生修正错误，解决方案是先对所有CSS文件进行变量替换，时间戳添加，再由r.js合并。这会降低处理速
        度但可以解决该问题。

        考虑到速度，此过程仅支持在build时进行，开发服务器访问时不能使用。

        所有静态资源路径都应该使用绝对路径，避免在CSS中引用相对路径的图像资源。
        '''

        #搜索所有CSS文件
        all_css_files=utils.FileSearcher(r'\.css$',self._build_css_dir,relative=False).search()

        #替换和加时间戳
        for dst in all_css_files:
            content=utils.readfile(dst)
            content=all_url(content,os.path.dirname(dst))
            content=replace(content,self._target)
            utils.writefile(dst,content)

        #仅对指定的CSS进行r.js合并
        css_modules=C('require_css_modules')
        if not utils.isList(css_modules):
            css_modules=['main']

        for css in css_modules:
            if not utils.isStr(css):
                continue;
            css = re.sub(r'\/*','',css)
            if not css.endswith('.css'):
                css+='.css'
            css_realpath=os.path.join(self._build_css_dir,css)
            self.build_css(css_realpath,css_realpath)
            continue

    @classmethod
    def build_css(self,src,dst):
        '''
        handle one css src to dst

        合并和按需压缩
        '''
        subprocess.call('node %s -o cssIn=%s out=%s'%(RJS_PATH,src,dst),shell=True)
        if self._compress:
            subprocess.call( 'java -jar ' + YC_PATH + ' --type css --charset ' + C('encoding') + ' ' + dst + ' -o ' + dst , shell=True )

    @classmethod
    def _js(self):
        '''
        handle js

        JS文件不同于CSS，其本身不能引用其它相对路径的静态资源，因此可以实现
        先合并再替换、加时间戳，无需预先处理所有js文件。
        '''
        js_modules=C('require_modules') or C('require_js_modules')
        if not utils.isList(js_modules):
            js_modules=['main']

        for js in js_modules:
            if not utils.isStr(js):
                continue;
            js=re.sub(r'^\/+','',js)
            if not js.endswith('.js'):
                js+='.js'
            js_realpath=os.path.join(self._build_js_dir,js)
            self.build_js(js_realpath,js_realpath,self._build_js_dir)

    @classmethod
    def build_js(self,src,dst,base_dir):
        '''
        handle one js src to dst

        合并、替换、加时间戳并按需压缩。
        '''
        js=os.path.relpath(src,base_dir)
        subprocess.call( 'node ' + RJS_PATH +' -o name=' + js[0:-3] + ' out='+ dst + ' optimize=none baseUrl='\
            + base_dir , shell=True)
        #repalce
        content=utils.readfile(dst)
        content=replace(content,self._target)
        utils.writefile(dst,content)
        if C('js_ascii_only'):
            subprocess.call( 'node ' + RPL_PATH +' '+dst+' '+dst,shell=True)
        if self._compress:
            subprocess.call( 'java -jar ' + YC_PATH + ' --type js --charset ' + C('encoding') + ' ' + dst + ' -o ' + dst , shell=True )
                
    @classmethod
    def _tpl(self):
        '''
        handle tempaltes

        模板仅需加时间戳和变量替换。

        这里需要加入额外的{compile_dir}文件夹下的文本文件。
        '''
        fs=utils.FileSearcher(r'\.%s$'%C('template_ext'),self._build_tpl_dir,relative=False)
        tpls=fs.search()
        if self._compile_dir:
            nfs=utils.FileSearcher(r'.+',self._build_compile_dir,relative=False)
            compile_files=nfs.search()
            for f in compile_files:
                mime=mimetypes.guess_type(f,False)
                content_type=mime[0] or 'text/plain'
                if not re.match(utils.BINARY_CONTENT_TYPE_KEYWORDS,content_type,re.I):
                    tpls.insert(0,f)

        for tpl in tpls:
            content = utils.readfile(tpl)
            #模板的静态资源相对目录应该写死为cwd，即资源路径应该始终是绝对路径
            content = html_link(content,'.')
            content = html_script(content,'.')
            content = html_img(content,'.')
            content = all_url(content,'.')
            content = replace(content,self._target)
            content = removeCssDepsDeclaration(content)
            utils.writefile(tpl,content)

    @classmethod
    def _html(self):
        '''
        generate html

        HTML直接以输出好的模板文件做渲染。

        由于数据原因个别子模板单独渲染会失败，这里用{html_force_output}变量
        可以跳过这类模板。

        TODO：考虑支持require_html_modules
        '''
        fs=utils.FileSearcher(r'\.%s$'%C('template_ext'),self._build_tpl_dir)
        tpls=fs.search()
        for tpl in tpls:
            try:
                tr = TokenRender(re.sub(r'\.%s$'%C('template_ext'),'',tpl))
                html = tr.render(True)#render(re.sub(r'\.%s$'%C('template_ext'),'',tpl),build=True)
                target_dir= os.path.join(self._build_html_dir,os.path.dirname(tpl))
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                dst_file=re.sub(r'\.%s$'%C('template_ext'),'.html',os.path.join(self._build_html_dir,tpl))
                utils.writefile(dst_file,html)
            except Exception,e:
                if not C('html_force_output'):
                    raise e
                else:
                    log.error(e)


if __name__ == '__main__':
    builder=UrsaBuilder(True,True,'online')
    builder.build()