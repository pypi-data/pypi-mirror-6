import base

################################################################################
################################### Classes ####################################
################################################################################
class ClientException(base.BaseClientException): pass

class Client(object):
    """
        Client class

        Variables:
        _ip             - Server ip
        _port           - Server port
        _retry          - Retry number
    """
    def __init__(self,ip,port,retry=3):
        self._ip = ip
        self._port = port
        self._retry = retry

    def runAction(self,action_class,data=None):
        """
            This command executes action on server with given data.

            Input:
            action_class    - Action class
            data            - Data to send to server

            Returns:
            Received data
        """
        import isockdata
        import action
        import inspect

        if not inspect.isclass(action_class) or not issubclass(action_class,action.Action): raise ClientException("First method argument must be Action subclass.")

        isock_data = isockdata.ISockData()
        isock_data.setActionClass(action_class)
        isock_data.setInputData(data)

        isock_data.from_string(self._sendAndReceive(isock_data.to_string()))
        if isock_data.getException() != None: raise isock_data.getException()

        return isock_data.getOutputData()

    def _sendAndReceive(self,data_to_send):
        """
            This function sends and receives data from server

            Input:
            data_to_send    - data to send

            Returns:
            Received data
        """
        client = base.BaseClient()
        error = None
        for retry in range(self._retry):
            client.open()
            try:
                client.connect(self._ip,self._port)
                client.send(data_to_send)
                data_received = client.receive()
            except base.ISockBaseException as error:
                continue
            else:
                break
            finally:
                client.close()
        else:
            raise ClientException("Retry limit exceeded. Error: " + str(error))

        return data_received