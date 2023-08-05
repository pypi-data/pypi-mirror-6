from producers import producer
from consumers import consumer
from constants import *
import time
import threading

def test_init_producer():
    p=producer('ipc:///tmp/test/0')
    assert p is not None
    assert p.sock() is not None
    p.close()
    
def test_init_consumer():
    p=producer('ipc:///tmp/test/0')
    def foo(message):
        pass
    c=consumer('ipc:///tmp/test/0',foo,JSON)
    assert p is not None
    assert p.sock() is not None
    assert c is not None
    assert c.sock() is not None
    p.close()
    c.close()    
    
def test_init_basic_consume():
    m = threading.Condition()
    m.acquire()
    p=producer('ipc:///tmp/test/0')
    def foo(message):
        m.acquire()
        assert message == 'test message'
        m.notifyAll()
        m.release()
    c=consumer('ipc:///tmp/test/0',foo,STRING)
    c.start()
    assert p is not None
    assert p.sock() is not None
    assert c is not None
    assert c.sock() is not None
    p.push('test message',STRING)
    m.wait() 
    m.release()
    c.stop()   
    c.close()        
    p.close()

