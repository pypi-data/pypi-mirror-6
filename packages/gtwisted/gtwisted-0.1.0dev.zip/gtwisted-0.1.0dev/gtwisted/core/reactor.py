#coding:utf8
'''
Created on 2014年2月19日

@author:  lan (www.9miao.com)
'''
from __future__ import division, absolute_import
from gevent import monkey; monkey.patch_os()

import sys
del sys.modules['gtwisted.core.reactor']
from twisted.internet import default
default.install()

    
    