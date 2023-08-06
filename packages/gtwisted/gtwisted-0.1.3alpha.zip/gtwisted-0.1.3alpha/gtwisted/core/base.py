#coding:utf8
'''
Created on 2014年2月21日
网络连接中的一些元素，定时器，端口监听器，连接者，通道等
@author:  lan (www.9miao.com)
'''
from gevent.server import StreamServer,DatagramServer
from gevent.pywsgi import WSGIServer
from gevent import Greenlet
import gevent

class DelayCall:
    """延迟调用对象
    """
    
    def __init__(self,f,*args,**kw):
        """
        """
        self.f = f
        self.args = args
        self.kw = kw
    
    def call(self):
        return self.f(*self.args,**self.kw)
    
class Timer(Greenlet):
    
    def __init__(self,seconds,f,*args,**kw):
        """以一个微线程的方式实现一个定时器
        """
        Greenlet.__init__(self)
        self.seconds = seconds
        self.delay_call = DelayCall(f,*args,**kw)
        
    def cancel(self):
        """取消定时器
        """
        self.kill()
        
    def _run(self):
        """
        """
        gevent.sleep(self.seconds)
        return self.delay_call.call()
        

class Transport:
    
    def __init__(self,skt,address,sessionno=0):
        """基础连接通道
        """
        self.skt = skt
        self.address = address
        self.sessionno = sessionno
        
    def getAddress(self):
        """获取地址
        """
        return self.address
        
    def close(self):
        """关闭通道连接
        """
        self.skt.close()
        
    def recv(self,*args):
        """接收消息
        """
        return self.skt.recv(*args)
    
    def sendall(self,data):
        """发送消息
        """
        return self.skt.sendall(data)


class BasePortListener(Greenlet):
    """基础的端口监听器
    """
    def __init__(self,port,factory,server_cls,port_type=""):
        """端口监听器
        """
        Greenlet.__init__(self)
        self.port = port
        self.factory = factory
        self.server_cls = server_cls
        self.port_type = port_type
        
    def getHost(self):
        """获取主机地址
        """
        return "0.0.0.0",self.port
    
    def getPortType(self):
        """获取端口类型
        """
        return self.port_type
    
    def _run(self):
        """启动监听器
        """
        ser = self.server_cls(self.getHost(),self.factory,backlog=100000)
        ser.serve_forever()
    

class TCPPortListener(BasePortListener):
    """TCP服务端（端口监听器）
    """
    
    def __init__(self,port,factory):
        """TCP服务端（端口监听器）
        """
        BasePortListener.__init__(self, port, factory, StreamServer,port_type="TCP")
        

class UDPPortListener(BasePortListener):
    """UDP服务端（端口监听器）
    """
    
    def __init__(self,port,factory):
        """
        """
        BasePortListener.__init__(self, port, factory, DatagramServer,port_type="UDP")
        
    
class WSGIPortListener(BasePortListener):
    """WSGI服务端（端口监听器）
    """
    def __init__(self,port,factory):
        """
        """
        BasePortListener.__init__(self, port, factory, WSGIServer,port_type="WSGI")
        
class BaseConnector(Greenlet):
    """基础连接器
    """
    
    def __init__(self,address,factory):
        """
        """
        Greenlet.__init__(self)
        self.address = address
        self.factory = factory
        
    def getHost(self):
        """获取主机地址
        """
        return self.address
        
    def connect(self):
        """开始连接
        """
        self.factory.startedConnecting(self)
        
    def _run(self):
        """
        """
        self.factory.doStart()
        
    

