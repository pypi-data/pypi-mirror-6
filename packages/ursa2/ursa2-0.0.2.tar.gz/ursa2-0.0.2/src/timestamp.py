#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
 timestamp.py

 changelog
 2013-12-01[15:59:50]:created
 2013-12-10[11:17:11]:clean

 @info yinyong,osx-x64,UTF-8,192.168.1.101,py,/Users/yinyong/work/ursa2/src
 @author yinyong@sogou-inc.com
 @version 0.0.1
 @since 0.0.1
'''
from conf import C,log
import re
import utils
import os
from replace import replace
from urlparse import urlparse,parse_qs

def _addtimestamp(content,reg,base_dir,force_abspath=False):
    '''
    以base_dir为基础目录，在content中搜寻匹配reg的URL并尝试追加时间戳
    
    reg:匹配URL的正则，其中\3为URL
    force_abspath:强制路径为绝对路径，即以WD为base_dir
    '''
    iters=re.finditer(reg,content,re.I|re.M)
    t=C('timestamp_name')
    for it in reversed(list(iters)):
        start = content[0:it.start(1)]
        url = it.group(3)
        end = content[it.end(1):]
        local_url = replace(url)
        parsed_url = urlparse(local_url,False)
        parsed_query = parse_qs(parsed_url.query)

        #已经有时间戳的不再添加
        #带协议的不再添加
        if not local_url or not parsed_url.path:
            continue
        elif re.match(r'^\s*(about:|data:|#)',local_url):
            log.warn('%s is an invalid url'%local_url)
            continue
        elif parsed_query.get(t) is not None:
            log.warn("%s has a timestamp"%local_url)
            continue
        elif parsed_url.scheme  or local_url.startswith('//'):
            log.warn("%s has a scheme"%local_url)
            continue

        if os.path.isabs(parsed_url.path) or force_abspath:
            #绝对路径，则以当前工程根目录为root
            timestamp=utils.get_file_timestamp(utils.abspath(parsed_url.path))
        else:
            #相对目录，则此当前文件目录为root
            #应该仅在CSS内使用相对路径
            timestamp=utils.get_file_timestamp(os.path.join(base_dir,parsed_url.path))

        parsed_url=urlparse(url,False)
        new_query=parsed_url.query
        if '' == new_query:
            new_query=t+"="+timestamp
        else:
            new_query+='&%s=%s'%(t,timestamp)
        if '' == parsed_url.fragment:
            new_fragment=''
        else:
            new_fragment='#'+parsed_url.fragment

        if not parsed_url.scheme:
            new_scheme = ''
        else:
            new_scheme=parsed_url.scheme+"://"

        new_url=new_scheme+parsed_url.netloc+parsed_url.path+'?'+new_query+new_fragment
        content=start+(it.group(2) or '')+new_url+(it.group(2) or '')+end

    return content

def html_link(content,base_dir="."):
    '''
    向<html>中<link>元素添加时间戳
    '''
    return _addtimestamp(content,r'<link.* href=(([\'"])(.*?\.css.*?)\2)',base_dir,force_abspath=True)

def html_script(content,base_dir="."):
    '''
    向<html>中<script>元素添加时间戳
    '''
    return _addtimestamp(content,r'<script.* src=(([\'"])(.*?\.js.*?)\2)',base_dir,force_abspath=True)

def html_img(content,base_dir='.'):
    '''
    向<html>中<img>元素添加时间戳
    '''
    return _addtimestamp(content,r'<img.* src=(([\'"])(.*?\.(png|gif|jpe?g|bmp|ico).*?)\2)',base_dir,force_abspath=True)

def all_url(content,base_dir="."):
    '''
    向HTML、CSS中的url()添加时间戳
    '''
    return _addtimestamp(content,r'url\((([\'"])?([\S]+?)\2?)\)',base_dir)

def all(content,base_dir='.'):
    '''
    添加所有类型的时间戳
    '''
    content=html_link(content,base_dir)
    content=html_script(content,base_dir)
    content=html_img(content,base_dir)
    content=all_url(content,base_dir)

    return content

if __name__ == '__main__':
    sample="url(@static_prefix@/www/js/main/ls.css?t=*&ty=09&bn==56#hjk)"
    print sample
    print all_url(sample)