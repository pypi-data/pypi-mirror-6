Description
===========
Util for launch any function in several threads.
Using:
    import Queue
    a = Queue.Queue
    
    @multithreaddecorator.MultiThreadDecorator(20)
    def f(b):
        import time
        time.sleep(1)
        b.put('one launch')
    for i in range(1000):
        f(a)
    
    while not f.is_over(): pass
