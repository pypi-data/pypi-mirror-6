# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Variety of classes, mixins, and functions for servers from low-level
sockets to high-level XMLRPC. These are focused on enhancing the
features of the L{SocketServer} class hierarchy.

@todo: The documentation for this file is unfortunately a bit lacking
toward the end.
"""

from exceps import *
from log import *
from threads import *
import select, socket, SimpleXMLRPCServer, SocketServer, threading, xmlrpclib

def spawn_server_thread( server ):
    """
    Calls L{spawn_thread} on the C{serve_forever} method of a given
    server.
    """
    return spawn_thread( server.serve_forever )

class NullXmlRpcServer( SimpleXMLRPCServer.SimpleXMLRPCServer ):
    """XML RPC Server that handles nulls."""
    allow_reuse_address = True
    def _marshaled_dispatch(self, data, dispatch_method = None):
        """
        This is copied over from the Python 2.4 standard library's
        L{SimpleXMLRPCServer}.

        Dispatches an XML-RPC method from marshalled (XML) data.

        XML-RPC methods are dispatched from the marshalled (XML) data
        using the _dispatch method and the result is returned as
        marshalled data. For backwards compatibility, a dispatch
        function can be provided as an argument (see comment in
        SimpleXMLRPCRequestHandler.do_POST) but overriding the
        existing method through subclassing is the prefered means
        of changing method dispatch behavior.
        """

        params, method = xmlrpclib.loads(data)

        # generate response
        try:
            if dispatch_method is not None:
                response = dispatch_method(method, params)
            else:
                response = self._dispatch(method, params)
            # wrap response in a singleton tuple
            response = (response,)
            response = xmlrpclib.dumps(response, methodresponse=1, allow_none=True)
        except xmlrpclib.Fault, fault:
            handle_exceptions()
            response = xmlrpclib.dumps(fault)
        except:
            # report exception back to server
            handle_exceptions()
            response = xmlrpclib.dumps(
                    xmlrpclib.Fault(1, "%s:%s" % (sys.exc_type, sys.exc_value))
                    )

        return response



class StoppableServerMixin( object ):
    """
    Mix-in class for SocketServers that checks periodically checks whether
    we should be exiting, and/or catches errors. To be able to stop
    all servers, the class keeps track of all instances.
    """

    servers = set()
    stop_event = threading.Event()

    @classmethod
    def stop_all( cls ):
        """Stops all servers."""
        cls.stop_event.set()
        for server in StoppableServerMixin.servers:
            server.stop()

    def __init__( self, timeout, do_catch ):
        """
        @param timeout: The amount of time to spend in C{select.select}.
        @type timeout: int

        @param do_catch: Whether exceptions should be swallowed in the loop.
        @type do_catch: bool
        """
        self.timeout = timeout
        self.do_catch = do_catch
        self.stop_event = threading.Event()

    def stop( self ):
        debug( 'commons.StoppableServerMixin.stop',
                "stop-event set for server", self )
        self.stop_event.set()

    def handle_stop( self ):
        """
        To be overridden in the subclass. This is called as soon as we
        exit the loop but before we close the socket and remove the
        server from the class' tracking set.
        """
        pass

    def serve_forever( self ):
        """
        Same as C{SocketServer.serve_forever}, but additionally checks
        on L{Thread.wait_stop} to see if all threads should terminate.

        Also catches exceptions to prevent errors from bringing down
        the server.
        """
        StoppableServerMixin.servers.add( self )
        while not self.stop_event.isSet():
            rd, wr, ex = select.select( [ self.socket.fileno() ],
                    [], [], self.timeout)
            if rd:
                if self.do_catch:
                    try:
                        self.handle_request()
                    except:
                        handle_exceptions()
                else:
                    self.handle_request()
            debug( 'commons.StoppableServerMixin.serve_forever',
                    'checking stop-event for server', self )
        debug( 'commons.StoppableServerMixin.serve_forever',
                'stopping server', self )
        self.handle_stop()
        self.socket.close()
        StoppableServerMixin.servers.remove( self )



class StreamServer( StoppableServerMixin, SocketServer.TCPServer ):
    """
    Base class for stoppable TCP stream servers.

    This class supports interrupts because it times out the blocking call to
    C{select.select}, and checks whether the program is terminating.
    """

    allow_reuse_address = True

    def __init__( self, host, port, handler, timeout, do_catch ):
        SocketServer.TCPServer.__init__( self, ( host, port ), handler )
        StoppableServerMixin.__init__( self, timeout, do_catch )



ThreadingMixin = SocketServer.ThreadingMixIn



class ThreadingStreamServer( ThreadingMixin, StreamServer ):
    """
    Generic TCP stream server that spawns a handler thread per request.
    """
    pass



class XmlRpcServer( StoppableServerMixin, NullXmlRpcServer ):
    def __init__( self, addr, timeout, do_catch ):
        # TODO which of these 2 is necessary?
        NullXmlRpcServer.allow_reuse_address = True
        XmlRpcServer.allow_reuse_address = True
        NullXmlRpcServer.__init__( self, addr = addr, logRequests = False )
        StoppableServerMixin.__init__( self, timeout, do_catch )



class MessageHandler( SocketServer.StreamRequestHandler ):
    """
    Handler for accepting and processing "messages."
    Messages are usually very short strings which require no response.
    This handler listens for the complete message before passing it onto the 
    """

    chunk_size = 4096

    def handle( self ):
        socket = self.request
        chunk = ' '
        chunks = []
        info( 'MessageHandler', 'handling message' )
        while ( len( chunk ) != 0 ):
            chunk = socket.recv( self.chunk_size )
            chunks.append( chunk )
        message = ''.join( chunks )
        self.handle_message( message )
        debug( 'MessageHandler', 'finished handling message' )

    def handle_message( self, message ):
        raise NotImplementedError()



class SocketStream( object ):
    """
    Tool for reading lines from a socket.
    """

    chunk_size = 4096

    def __init__( self, socket ):
        self.socket = socket

    def xreadlines( self ):
        """
        Yields lines as they are received via the socket.
        Does NOT include the trailing newline character(s).
        """
        buffer = []
        while True:
            chunk = self.socket.recv( self.chunk_size )
            if len( chunk ) == 0:
                break
            lines = chunk.split( '\n' )
            buffer.append( lines[ 0 ] )
            if len( lines ) > 1:
                yield ''.join( buffer )
                for line in lines[ 1 : -1 ]:
                    yield line
                buffer = [ lines[ -1 ] ]



class StreamClientSocket( socket.socket ):
    """
    Generic TCP stream client.
    """

    def __init__( self, host, port ):
        socket.socket.__init__( self, socket.AF_INET, socket.SOCK_STREAM )
        socket.socket.connect( self, ( host, port ) )



class StopException( Exception ): pass

class EndOfStream( Exception ): pass

# TODO rename this to 'supersocket' or some such
def stoppable_socket( sock ):
    orig_recv = sock.recv
    def new_recv(n):
        while True:
            try:
                result = orig_recv(n)
            # TODO filter this to that particular error
            except socket.timeout:
                debug( 'commons.stoppable_socket',
                       'checking stop-event for socket', sock )
                # TODO clean up the 'stopping' design
                if StoppableServerMixin.stop_event.isSet():
                    debug( 'commons.stoppable_socket', 'raising' )
                    raise StopException()
            else:
                if result == '':
                    raise EndOfStream()
                return result
    sock.recv = new_recv
    sock.settimeout( stoppable_server_check_interval )
    return sock



class StoppableRequestHandler( SocketServer.BaseRequestHandler ):
    def handle( self ):
        sock = stoppable_socket( self.request )
        return self.handle_loop()
