#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
 deps.py

 changelog
 2013-12-02[15:48:27]:created
 2013-12-14[12:18:46]:include collection supported

 @info yinyong,osx-x64,UTF-8,10.129.173.95,py,/Users/yinyong/work/ursa2/src
 @author yanni4night@gmail.com
 @version 0.0.1
 @since 0.0.1
'''
import re
import utils
import os
from conf import C,log

class DepsFinder(object):
    '''
    递归搜索指定模板文件的依赖模板
    '''
    @classmethod
    def __init__(self,tpl):
        '''
        tpl:模板，相对于template_dir目录
        '''
        self._result = []
        self._include_result = []
        #x=>x.tpl
        if not tpl.endswith('.%s'%C('template_ext')):
            tpl += '.%s'%C('template_ext')
        self._tpl = tpl
        self._history = {}
        self._done = False
        self._pattern = re.compile(r'\{%\s*(include|extends)\s+([\'"])([\w\/\\\.-]+\.'+C('template_ext')+r')\2\s*%\}',re.I|re.M)

    @classmethod
    def _search(self,tpl):
        '''
        递归搜索
        '''
        try:
            #/x.tpl=>x.tpl
            # tpl=re.sub(r'^\/+','',tpl)
            abspath = utils.abspath(os.path.join(C('template_dir'),tpl))
            
            # if self._history.get(abspath) is not None:
            #     return
            # else:
            #     self._result.append(tpl)
            #     self._history[abspath]=1

            content = utils.readfile(abspath)
            iters = re.finditer(self._pattern,content)

            for i in reversed(list(iters)):
                tpl = utils.filterRelPath(i.group(3))
                #abspath=utils.abspath(os.path.join(C('template_dir'),tpl))
                if self._history.get(tpl) is None:
                    self._result.append(tpl)
                    self._history[tpl] = 1
                    if 'include' == i.group(1):
                        self._include_result.append(tpl)
                    self._search(tpl)

        except Exception, e:
            log.error('[deps]%s'%e)

    @classmethod
    def find(self):
        '''
        获取依赖的接口
        '''
        if not self._done:
            self._search(self._tpl)
        self._done = True
        return self._result;

    @classmethod
    def findIncludes(self):
        '''
        获取依赖的接口
        '''
        if not self._done:
            self.find()
        return self._include_result;

    @classmethod
    def get_tpl():
        '''
        '''
        return self._tpl

    @classmethod
    def __del__(self):
        self._history = {}
        self._result = []

if __name__ == '__main__':
    df=DepsFinder(u'/template/index')
    print df.findIncludes()
