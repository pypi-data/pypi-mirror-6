#!/usr/bin/env python
#coding:utf8
#author:zhoujingjiang
#date:2013-1-4
#comment:工具函数模块

from ConfigParser import ConfigParser
import imp
import sys
import types

import chardet

class ConfigParser(ConfigParser):
    def optionxform(self, option_str):  
        return option_str

def str2unicode(s):
    if isinstance(s, str):
        code = chardet.detect(s)
        if code['confidence'] > 0.5:
            return unicode(s, code['encoding'])
    return s

def config2dict(config_file, section=None, decode=False):
    '''将配置文件的内容读进字典'''
    cf = ConfigParser()
    cf.read(config_file)

    sections = [section]
    if section is None:
        sections = cf.sections()

    ret_dic = {}
    for sec in sections:
        if decode: 
            ret_dic[str2unicode(sec)] = dict(
                    map(lambda seq:map(str2unicode, seq), 
                        cf.items(sec)))
        else:
            ret_dic[sec] = dict(cf.items(sec))

    return ret_dic.pop(
            str2unicode(section) if decode else section) \
            if section is not None else ret_dic

def load_module(name, path=None, add_to_sys=False):
    '''动态导入或reload一个模块'''
    mod = imp.load_module(name, *imp.find_module(name, path))
    if add_to_sys:
        sys.modules[name] = mod
    return mod

