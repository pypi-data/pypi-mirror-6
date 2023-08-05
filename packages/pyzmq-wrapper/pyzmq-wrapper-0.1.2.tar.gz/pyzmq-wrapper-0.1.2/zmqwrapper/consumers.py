import zmq
from sockets import ClientConnection
from constants import *
import threading

def consumer(address,callback,message_type):
    """
    Creates a consumer binding to the given address pull messages.
    The callback is invoked for every reply received.

        Args:
            - address: the address to bind the PULL socket to.
            - callback: the callback to invoke for every message. Must accept 1 variables - the message
            - message_type: the type of message to receive
    """
    return Consumer(address,callback,message_type)
    
class Consumer(ClientConnection):
    """
    Requestor that that can send requests of given type
    
        Args:
            - address: the address to bind to
            - callback: the callback to invoke for every reply
            - message_type: the type of request to send
    """
        
    def __init__(self,address,callback,message_type):
        self._active = True
        self._callback = callback
        self._message_type = message_type
        super(Consumer,self).__init__(address,zmq.PULL)
        
                    
    def _consume(self):
        while self._active:
            try:
                topic, message=super(Consumer,self).receive(self._message_type)
                #process the message
                self._callback(message)
            except zmq.ZMQError:
                pass
    
    
    def start(self):
        """
        Start a thread that consumes the replies and invokes the callback
        """
        t=threading.Thread(target=self._consume)
        t.start()
        
    def stop(self):
        """
        Stop the consumer thread
        """
        self._active = False            
