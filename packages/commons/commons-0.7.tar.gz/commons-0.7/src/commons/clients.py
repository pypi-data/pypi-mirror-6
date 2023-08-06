# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Simple clients (built on synchronous sockets).
"""

import socket
from commons.log import *

class PersistentSender( object ):
    """
    A simple wrapper around a socket which re-connects if necessary.
    """
    def __init__( self, host, port, init_msg ):
        """
        @param host: Host to connect to.
        @type host: str
        @param host: Port to connect to.
        @param port: int
        @param init_msg: The message to be sent on reconnection.
        @param init_msg: str
        """
        self.addr = ( host, port )
        self.init_msg = init_msg
        self.socket = None

    def send( self, msg ):
        """
        Whenever a connection is lost, it tries to resend.
        If a connection cannot be established, the message is discarded.
        """
        try:
            if self.socket is None:
                debug( 'PersistentSender', '(re)connecting to', self.addr )
                self.socket = socket.socket()
                self.socket.connect( self.addr )
                self.socket.send( self.init_msg )
            self.socket.send( msg )
        except socket.error, ex:
            debug( 'PersistentSender', 'no connection:', ex )
            self.socket = None

    def close( self ):
        """
        Closes the socket (if it's connected).
        """
        if self.socket is not None:
            self.socket.close()
