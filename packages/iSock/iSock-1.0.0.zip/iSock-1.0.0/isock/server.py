import base

################################################################################
################################### Classes ####################################
################################################################################
class ServerException(base.BaseServerException): pass

class Server(base.BaseServer):
    """
        Socket Server class

        Variables:
        _actions        - List of actions that client can invoke
    """
    def __init__(self,ip,port):
        import threading

        self._actions = []

        try: base.BaseServer.__init__(self,(ip,port),ServerHandler)
        except base.BaseServerException as error: raise ServerException(error)

    def addAction(self,action_object):
        """
            Reqisters server action

            Input:
            action      - Action that client can perform

            Returns:
            Nothing
        """
        import action

        if not isinstance(action_object,action.Action): raise ServerException("Input action object has to be instance of Action subclass. " + str(type(action_object)))

        try: self.findAction(type(action_object))
        except ServerException: self._actions.append(action_object)
        else:
            raise ServerException("Action is already registered. " + str(type(action_object)))

    def findAction(self,action_class):
        """
            This function finds and returns action that is an instance of action_class

            Input:
            action_class        - Action class

            Retruns:
            action              - Action object
        """
        for action in self._actions:
            if type(action) == action_class: return action
        else:
            raise ServerException("Cannot find action: " + str(action_class))

class ServerHandler(base.BaseRequestHandler):
    """
        Socket Server handler class

        Variables:
        server      - Socket Server reference
    """

    def handle(self):
        """
            Handles all clients requests

            Input:
            Nothing

            Returns:
            Nothing
        """
        import isockdata

        isock_data = isockdata.ISockData()

        try: isock_data.from_string(self.receive());
        except base.ISockBaseException as error: isock_data.setException(error)
        else:
            try: action = self.server.findAction(isock_data.getActionClass())
            except ServerException as error: isock_data.setException(error)
            else:
                try: isock_data.setOutputData(action.action(isock_data.getInputData()))
                except Exception as error: isock_data.setException(error)

        isock_data.setInputData(None) # Don't send client data back to client.

        try: self.send(isock_data.to_string())
        except base.ISockBaseException as error: pass
