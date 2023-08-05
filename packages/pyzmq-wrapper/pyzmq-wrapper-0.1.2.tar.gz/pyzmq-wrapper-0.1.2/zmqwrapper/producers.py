import zmq
from sockets import ServerConnection
from constants import *
import threading

def producer(address):
    """
    Creates a producer binding to the given address push messages.
    The callback is invoked for every request received.

        Args:
            - address: the address to bind the PUSH socket to.
    """
    return Producer(address)
    
class Producer(ServerConnection):
    """
    Requestor that that can respond to requests of given type
    
        Args:
            - address: the address to bind to
    """
        
    def __init__(self,address):
        self._active = True
        super(Producer,self).__init__(address,zmq.PUSH)
        
                    
    def push(self,message,message_type):
        """
        Send a reply message of the given type
        
        Args:
            - message: the message to publish
            - message_type: the type of message being sent
        """
            
        super(Producer,self).send(message,message_type)
    
