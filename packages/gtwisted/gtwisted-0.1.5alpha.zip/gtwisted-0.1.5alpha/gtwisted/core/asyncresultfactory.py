#coding:utf8
'''
Created on 2014年2月22日
异步结果工厂
@author:  lan (www.9miao.com)
'''
from gtwisted.utils.singleton import Singleton
from gevent.event import AsyncResult
import hashlib

def _makeUniqueKey(aresult):
    """为AsyncReuslt对象生成一个唯一的key
    """
    md_first = hashlib.md5()
    _key = str(id(aresult))
    md_first.update(_key)
    key_last = md_first.hexdigest()
    return key_last
    

class AsyncResultFactory:
    """异步结果工厂,用来产生AsyncResult对象，并且生成一个唯一的key存放async_reuslts中
    """
    
    __metaclass__ = Singleton
    
    def __init__(self):
        """
        @param async_reuslts: dict 又来存放产生的AsyncResult对象
        """
        self.async_reuslts = {}
        
    def createAsyncResult(self):
        """产生一个AsyncResult对象
        """
        _async_result = AsyncResult()
        _key = _makeUniqueKey(_async_result)
        self.async_reuslts[_key] = _async_result
        return _key,_async_result
    
    def dropAsyncResultByKey(self,_key):
        """清除存储在async_reuslts中记录
        """
        if self.async_reuslts.has_key(_key):
            del self.async_reuslts[_key]
            
    def popAsyncResult(self,_key):
        """清除存储在async_reuslts中记录，并返回_key对应的AsyncResult对象
        """
        a = self.async_reuslts.get(_key)
        self.dropAsyncResultByKey(_key)
        return a
        
        
        
        