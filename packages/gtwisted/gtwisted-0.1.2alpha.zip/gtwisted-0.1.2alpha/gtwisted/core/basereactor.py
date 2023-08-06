#coding:utf8
'''
Created on 2014年2月21日
Reactor 的基类
@author:  lan (www.9miao.com)
'''

class BaseReactor:
    """模拟twisted中的reactor，作为统一的管理去监听一个端口，去作为客户端连接某个服务，开启一个新的计时器等。
    """
    
    def __init__(self):
        """
        """
        pass
    
    def listenTCP(self,port,factory):
        """监听一个端口
        @param port: int 监听的端口
        @param factory: Fctory 处理客户端消息的工厂
        """
        pass
    
    def connectTCP(self,host,port,factory,timeout=30):
        """连接一个远程服务端
        @param host: str 主机的地址
        @param port: int 监听的端口
        @param factory: Fctory 处理客户端消息的工厂
        @param backlog: int 可阻塞等待的连接数
        """
        pass
    
    def callLater(self,seconds,f, *args, **kw):
        """添加一个定时器
        @param seconds: float 定时器设定的时间
        @param f: func 定时器执行的方法
        @param args: 魔法参数，定时器调用方法所需的参数
        @param kw: 魔法默认参数，定时器调用方法所需的默认参数
        """
        assert callable(f), "%s is not callable" % f
        assert seconds >= 0,"%s is not greater than or equal to 0 seconds" % (seconds,)
        pass
    
    def start(self):
        """作为主的运行携程
        """
        pass
    
    def run(self):
        """运行reactor
        """
        pass
        
    def stop(self):
        """停止运行reactor
        """
        pass
    
    def callWhenStop(self,f,*args,**kw):
        """当reactor停止运行时调用方法
        @param f: func 执行的方法
        @param args: 魔法参数，f方法所需的参数
        @param kw: 魔法默认参数，f法所需的默认参数
        """
        pass
    
    def callWhenRunning(self,f,*args,**kw):
        """当reactor运行时调用方法
        @param f: func 定时器执行的方法
        @param args: 魔法参数，f方法所需的参数
        @param kw: 魔法默认参数，f方法所需的默认参数
        """
        pass
    
def install():
    """装载BaseReactor为服务的reactor
    """
    reactor = BaseReactor()
    from gtwisted.core.installer import installReactor
    installReactor(reactor)

