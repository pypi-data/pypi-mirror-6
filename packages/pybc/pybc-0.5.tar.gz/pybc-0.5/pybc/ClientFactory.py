"""
ClientFactory.py: contains the ClientFactory class.

"""
import logging
from twisted.internet import protocol

from pybc.BlockchainProtocol import BlockchainProtocol

class ClientFactory(protocol.ClientFactory):
    """
    This is a Twisted client factory, responsible for making outgoing
    connections and starting Clients to run them. It is part of a Peer.
    
    """
    
    def __init__(self, peer):
        """
        Make a new ClientFactory with a reference to the Peer it is producing
        outgoing connections for.
        
        """
        
        # Keep the peer around
        self.peer = peer
        
    def buildProtocol(self, addr):
        """
        Make a new client protocol. It's going to be connecting to the given
        address.
        
        """
        
        logging.info("Client made connection to {}".format(addr))
        
        # Make a new BlockchainProtocol that knows we are its factory. It will
        # then talk to our peer.
        return BlockchainProtocol(self, (addr.host, addr.port))
        
    def clientConnectionLost(self, connector, reason):
        """
        We've lost a connection we made.
        
        """
        
        # Record that the outgoing connection is gone
        self.peer.lost_outgoing_connection(connector.getDestination().host)
        
        logging.warning("Lost outgoing connection.  Reason: {}".format(reason))

    def clientConnectionFailed(self, connector, reason):
        """
        We failed to make an outgoing connection.
        
        """
        
        # Record that the outgoing connection is gone
        self.peer.lost_outgoing_connection(connector.getDestination().host)
        
        logging.warning("Outgoing connection failed. Reason: {}".format(reason))
