import base
import SocketServer

######################################################################################
################################### Classes ##########################################
######################################################################################

class BaseServerException(base.ISockBaseException): pass

class BaseServer(SocketServer.ThreadingTCPServer):
    def __init__(self,address,handler):
        import socket

        try: SocketServer.ThreadingTCPServer.__init__(self,address,handler)
        except socket.error as error: raise BaseServerException(error)

