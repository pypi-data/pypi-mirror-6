#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
 setup.py

 changelog
 2013-11-30[00:06:29]:created
 2013-12-16[20:56:26]:upgrade to 0.0.2

 @info yinyong,osx-x64,UTF-8,192.168.1.101,py,/Users/yinyong/work/ursa2
 @author yanni4night@gmail.com
 @version 0.0.2
 @since 0.0.1
'''

from setuptools import setup, find_packages
from src.__init__ import __version__ as version
import os

dirs = ['assets','tpl']

data_files = []
for d in dirs:
    for dirpath, dirnames , filenames in os.walk(d):
        data_files.append( [ dirpath , [ os.path.join(dirpath , f) for f in filenames ] ] )

setup(
    name = "ursa2",
    version = version,
    packages = ['src'],
    data_files = data_files,
    install_requires = ['docopt>=0.6.1','jinja2>2.6','requests>=2.0.0'],
    package_data = {},
    author = "Yanni Nightingale",
    author_email = "yanni4night@gmail.com",
    description = "Ursa2 is an enhanced version of ursa which is a powerful front web developing environment.",
    license = "MIT",
    keywords = "ursa,fe,develop,web,jinja2,build",
    url = "https://github.com/yanni4night/ursa2",
    entry_points = {
        'console_scripts':[
            'ursa2=src.main:run'
            ]
        }
)