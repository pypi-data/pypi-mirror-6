######################################################################################
################################### Classes ##########################################
######################################################################################
class ISockBaseException(Exception): pass

class Base(object):
    """
        This class is responsible for low level communication

        Constants:
        BUFFER_SIZE     - Receive buffer size
        __HANDSHAKE     - Acknowledge string used to handshake

        Variable:
    """
    BUFFER_SIZE = 8192
    __HANDSHAKE = b'ISOCK_HANDSHAKE'

    def send(self,data):
        """
            This function sends data.
            Transmission protocol:
            <-- data length
            --> handshake acknowledge
            <-- data
            --> handshake acknowledge

            Input:
            date        - data to send

            Returns:
            Nothing
        """
        if not isinstance(data, str):
            raise ISockBaseException(str(type(data)) + " is wrong type. Data to send has to be string")

        data_length = len(data)
        self._send(str(data_length))
        data_received = self._recv(len(self.__HANDSHAKE))

        if data_received != self.__HANDSHAKE:
            raise ISockBaseException("Sending error. Data size. Did not received handshake acknowledge. Received: " + data_received)

        sent_data_lenght = 0
        while sent_data_lenght < data_length:
            sent_data_lenght += self._send(data[sent_data_lenght:])

        data_received = self._recv(len(self.__HANDSHAKE))

        if data_received != self.__HANDSHAKE:
            raise ISockBaseException("Sending error. Data load. Did not received handshake acknowledge. Received: " + data_received)

    def receive(self):
        """
            This function receives data.
            Transmission protocol:
            --> data length
            <-- handshake acknowledge
            --> data
            <-- handshake acknowledge

            Input:
            Nothing

            Returns:
            data        - Received data
        """
        data_received = self._recv(self.BUFFER_SIZE)

        try: data_length = int(data_received)
        except ValueError: raise ISockBaseException("Received data length is invalid.")

        self._send(self.__HANDSHAKE)

        received_data_length = 0
        data_received = ""
        while received_data_length < data_length:
            data = self._recv(self.BUFFER_SIZE)
            data_received = data_received + data
            received_data_length = len(data_received)

        self._send(self.__HANDSHAKE)

        return data_received

    def close(self):
        """
            This function closes socket connection

            Input:
            Nothing

            Returns:
            Nothing
        """
        self._close()

    def open(self):
        """
            This function opens socket

            Input:
            Nothing

            Returns:
            Nothing
        """
        self._open()

    def _recv(self,buffer):
        """
            Low level receive function.
            NOTE: This function has to be overloaded in class that inharits from this

            Input:
            buffer  - Buffer size

            Returns:
            Received data
        """
        raise ISockBaseException("_recv function not implement")

    def _send(self,data):
        """
            Low level send function.
            NOTE: This function has to be overloaded in class that inharits from this

            Input:
            data    - data to send

            Returns:
            Send data size
        """
        raise ISockBaseException("_send function not implement!")

    def _open(self):
        """
            Low level open socket function
            NOTE: This function has to be overloaded in class that inharits from this

            Input:
            Nothing

            Returns:
            Nothing
        """
        raise ISockBaseException("_open function not implement")

    def _close(self):
        """
            Low level close function.
            NOTE: This function has to be overloaded in class that inharits from this

            Input:
            Nothing

            Returns:
            Nothing
        """
        raise ISockBaseException("_close function not implement")
