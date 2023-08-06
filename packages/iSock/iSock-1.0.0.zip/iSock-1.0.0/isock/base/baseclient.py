import base

######################################################################################
################################### Classes ##########################################
######################################################################################

class BaseClientException(base.ISockBaseException): pass

class BaseClient(base.Base):
    """
        This class is responsible for Client communication

        Constants:

        Variables:
        socket_reference    - socket handle
    """
    def __init__(self):
        self.socket_reference = None

    def connect(self,ip,port):
        """
            This function connects to ip on port.
            It retrys MAX_RETRY times.

            Variables:
            ip          - Ip address
            port        - port

            Returns:
            Nothing
        """
        import time
        import socket

        try:
            self.socket_reference.connect((ip, port))
        except socket.error:
            self.close()
            reload(socket)
            raise BaseClientException(ip + ":" + str(port) + " is not responding.")

    def _recv(self,buffer):
        """
            Low level receive function.

            Input:
            buffer  - Buffer size

            Returns:
            Received data
        """
        import socket

        try: data = self.socket_reference.recv(buffer)
        except socket.error as error: raise BaseClientException(str(error))

        return data

    def _send(self,data):
        """
            Low level send function.

            Input:
            data    - data to send

            Returns:
            Send data size
        """
        import socket

        try: size = self.socket_reference.send(data)
        except socket.error as error: raise BaseClientException(str(error))

        return  size

    def _close(self):
        """
            Low level close function.

            Input:
            Nothing

            Returns:
            Nothing
        """
        self.socket_reference.close()

    def _open(self):
        """
            Low level open function.

            Input:
            Nothing

            Returns:
            Nothing
        """
        import socket
        self.socket_reference = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
