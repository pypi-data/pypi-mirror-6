#coding:utf8
'''
Created on 2014年2月22日

@author:  lan (www.9miao.com)
'''
from gtwisted.core import reactor
from gtwisted.core.rpc import PBServerProtocl,PBServerFactory
from gtwisted.utils import log
import sys
import gevent


class MyPBServerProtocl(PBServerProtocl):
    
    def remote_getResult(self,a,b):
        gevent.sleep(8)
        return a+b
        
class MyPBServerFactory(PBServerFactory):
    
    protocol = MyPBServerProtocl
    
reactor.listenTCP(9090, MyPBServerFactory())
log.startLogging(sys.stdout)
reactor.run()
