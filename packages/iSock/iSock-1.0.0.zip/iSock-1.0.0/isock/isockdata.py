import base

################################################################################
################################### Classes ####################################
################################################################################
class ISockDataException(base.ISockBaseException): pass

class ISockData(object):
    """
        Data container for data transfer

        Variables:
        _input_data         - Input data which are going to be send to server
        _output_data        - Output data that are produced on server
        _action_class       - Action class
        _exception          - Exception that was raised on server

    """
    def __init__(self):
        self._input_data = None
        self._output_data = None
        self._action_class = None
        self._exception = None

    def setActionClass(self,action_class):
        """
            This function sets action class

            Input:
            action_class    - Action class ref

            Returns:
            Nothing
        """
        self._action_class = action_class

    def getActionClass(self):
        """
            This function returns action class

            Input:
            Nothing

            Returns:
            action class
        """
        return self._action_class

    def setInputData(self,data):
        """
            This function sets input data

            Input:
            data            - data to send

            Returns:
            Nothing
        """
        self._input_data = data

    def getInputData(self):
        """
            This function returns input data

            Input:
            Nothing

            Returns:
            data
        """
        return self._input_data

    def setOutputData(self,data):
        """
            This function sets output data

            Input:
            data        - Data to send to client

            Returns:
            Nothing
        """
        self._output_data = data

    def getOutputData(self):
        """
            This function returns output data

            Input:
            Nothing

            Returns:
            data
        """
        return self._output_data

    def setException(self,exception):
        """
            This function sets exception

            Input:
            exception       - Exception that was raised

            Returns:
            Nothing
        """
        self._exception = exception

    def getException(self):
        """
            This function returns exception

            Input:
            Nothing

            Returns:
            exception
        """
        return self._exception

    def to_string(self):
        """
            This function saves object to string

            Input:
            Nothing

            Returns:
            string
        """
        import cPickle

        try: return cPickle.dumps(self)
        except cPickle.PicklingError as error: raise ISockDataException(error)

    def from_string(self,string_data):
        """
            This function restors object from string

            Input:
            string_data     - String data

            Returns:
            Nothing
        """
        import cPickle

        try: data = cPickle.loads(string_data)
        except cPickle.UnpicklingError as error: raise ISockDataException(error)

        self.setActionClass(data.getActionClass())
        self.setInputData(data.getInputData())
        self.setOutputData(data.getOutputData())
        self.setException(data.getException())
