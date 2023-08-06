#coding:utf8
'''
Created on 2014年2月20日
协议、工厂
@author:  lan (www.9miao.com)
'''
from gtwisted.core.base import Transport
from gevent import Greenlet
import gevent
from gevent import Timeout
from gevent.socket import create_connection
from gtwisted.utils import log
import socket

class BaseProtocol(Greenlet):
    
    def __init__(self,transport,factory):
        """
        """
        Greenlet.__init__(self)
        self.transport = transport
        self.factory = factory
        
    def connectionMade(self):
        """当连接建立时的处理
        """
        pass
        
    def connectionLost(self,reason):
        """当连接断开时的处理
        """
        pass
        
    def dataReceived(self, data):
        """当连接数据到达时的处理
        @param data: str 接收到的数据
        """
        pass
        
    def _run(self):
        """
        """
        self.connectionMade()
        try:
            while True:
                data = self.transport.recv(1024)
                if not data:
                    break
                gevent.spawn(self.dataReceived,data)
#                 self.dataReceived(data)
        except Exception,e:
            if not isinstance(e, socket.error):
                log.err()
            self.connectionLost(reason=e)
        else:
            self.connectionLost(reason=None)
        finally:
            self.transport.close()
            self.kill()
    
class ServerFactory:
    
    protocol = BaseProtocol
    
    def __init__(self):
        """
        @param sessionno: int 用来记录客户端连接的动态编号
        """
        self.sessionno = 0
        
    def buildProtocol(self, transport):
        """
        """
        pass
    
    def __call__(self,socket,address):
        """每当有客户端连接产生是会被调用
        """
        t = Transport(socket,address,self.sessionno)
        self.buildProtocol(t)
        p = self.protocol(t,self)
        p.start()
        self.sessionno +=1
        
class ClientFactory:
    
    protocol = BaseProtocol
    
    def __init__(self):
        """
        """
        self._protocol = None
        
    def buildProtocol(self, transport):
        """
        """
        pass
    
    def startedConnecting(self,connector):
        """
        """
        address = connector.getHost()
        client = create_connection(address)
        t = Transport(client,address)
        self.buildProtocol(t)
        self._protocol = self.protocol(t,self)
    
    def doStart(self):
        """
        """
        self._protocol.start()
        
        
        
    