#coding:utf8
'''
Created on 2014年2月22日

@author:  lan (www.9miao.com)
'''
from gtwisted.core.greactor import GeventReactor
from gtwisted.core.rpc import PBClientProtocl,PBClientFactory
from gtwisted.utils import log
import sys
reactor = GeventReactor()


class MyPBClientProtocl(PBClientProtocl):
    
    def remote_getResult(self,a,b):
        return a+b
        
class MyPBClientFactory(PBClientFactory):
    
    protocol = MyPBClientProtocl
    
client = MyPBClientFactory()

def printok():
    print "ok"
    reactor.callLater(1, printok)
    
def callRemote():
    dd = client.getRootObject()
    result = dd.callRemoteForResult('getResult',8,9)
    print result

reactor.connectTCP('localhost', 9090, client)
reactor.callLater(5, callRemote)
reactor.callLater(1, printok)
reactor.callLater(20, reactor.stop)
log.startLogging(sys.stdout)
reactor.run()


