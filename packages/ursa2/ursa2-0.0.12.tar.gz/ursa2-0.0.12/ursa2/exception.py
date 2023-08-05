#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
 exception.py

 changelog
 2013-12-07[12:46:58]:created

 custom defined exceptions and errors

 @info yinyong,osx-x64,UTF-8,192.168.1.104,py,/Users/yinyong/work/ursa2/src
 @author yanni4night@gmail.com
 @version 0.0.1
 @since 0.0.1
'''
class ConfigurationError(Exception):
    '''
    ConfigurationError
    '''
    @classmethod
    def __init__(self, msg):
        self.msg=msg
    @classmethod
    def __str__(self):
        return self.msg

class DirectoryError(Exception):
    '''
    DirectoryError
    '''
    @classmethod
    def __init__(self,msg):
        self.msg=msg
    @classmethod
    def __str__(self):
        return self.msg

class FileSizeOverflowError(Exception):
    '''
    File size overflow Error
    '''
    @classmethod
    def __init__(self,msg):
        self.msg=msg
    @classmethod
    def __str__(self):
        return self.msg
        