#coding=utf-8

__author__ = 'Dmitriy Shikhalev'
__author_email__ = 'dmitriy.shikhalev@gmail.com'
__version__ = '0.0.1'


from threading import Thread, RLock
import Queue

def MultiThreadDecorator(thread_amount):
    """
        Decorator for multithreading launch of some function.
        Usage:
            @MultiThreadDecorator(TREAD_AMOUNT)
            def SomeFunction(...):
                ...
            
            while not SomeFunction.is_over(): pass
            
            THREAD_AMOUNT is amount of possible threads in which you want SomeFunction run
    """
    
    class _MultiThreadDecorator(object):
        def __init__(self, func):
            self._func = func
            self._lock = RLock()
            self._threads = list()
            self._queue = Queue.Queue()
        def _workFunction(self):
            try:
                while True:
                    temp = self._queue.get(timeout=0)
                    args = temp['args']
                    kwargs = temp['kwargs']
                    
                    self._func(*args, **kwargs)
            except Queue.Empty:
                pass
        def __call__(self, *args, **kwargs):
            with self._lock:
                self._queue.put(dict(args=args, kwargs=kwargs))
                
                if len(self._threads) >= thread_amount:
                    for i, thread in enumerate(self._threads):
                        if not thread.isAlive():
                            del self._threads[i]
                            break
                else:
                    thread = Thread(target=self._workFunction)
                    thread.start()
                    self._threads.append(thread)
        def is_over(self):
            for thread in self._threads:
                if thread.isAlive(): return False
            else: return True
    
    return _MultiThreadDecorator

if __name__ == '__main__':
    import time
    print 'Testing of MultiThreadDecorator.\nNow run function foo(i) in 20 threads with 1 second interval'
    @MultiThreadDecorator(20)
    def foo(i):
        time.sleep(1)
        print 'foo', i
    
    for i in range(100):
        foo(i)
