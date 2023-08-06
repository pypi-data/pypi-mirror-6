import unittest
import isock

######################################################################################
################################### Helper Classes ###################################
######################################################################################
class _echo(isock.Action):
    def action(self,data):
        return data

class _serverVar(isock.Action):
    def __init__(self,server_variable):
        self.server_variable = server_variable

    def action(self,data):
        return self.server_variable

class _notAction1(object): pass
class _notAction2: pass

######################################################################################
################################### Test Classes #####################################
######################################################################################
class ISockBasic(unittest.TestCase):
    def setUp(self):
        import threading

        try: self.server = isock.Server("localhost",4440)
        except isock.ServerException as error: self.fail("Init Error" + str(error))

        self.server.addAction(_echo())

        server_variable = "dummy"
        self.server.addAction(_serverVar(server_variable))

        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def test_ISockBasic(self):
        client = isock.Client("localhost",4440)
        data_to_send = "dummy"
        received_data = client.runAction(_echo,data_to_send)
        self.assertEqual(data_to_send,received_data)

        received_data = client.runAction(_serverVar)
        self.assertEqual("dummy",received_data)

class ISockServerException(unittest.TestCase):
    def test_ISockServerException(self):
        import threading

        try: server = isock.Server("localhost",4441)
        except isock.ServerException as error: self.fail("Init Error" + str(error))

        server.addAction(_echo())

        with self.assertRaises(isock.ServerException):
            server.addAction(_echo())

        with self.assertRaises(isock.ServerException):
            server.addAction(_notAction1())

        with self.assertRaises(isock.ServerException):
            server.addAction(_notAction2())

        thread = threading.Thread(target=server.serve_forever)
        thread.start()

        server.shutdown()
        server.server_close()

class ISockPortTaken(unittest.TestCase):
    def test_ISockPortTaken(self):
        import threading

        try: server = isock.Server("localhost",4442)
        except isock.ServerException as error: self.fail("Init Error" + str(error))

        with self.assertRaises(isock.ServerException):
            server2 = isock.Server("localhost",4442)

        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        server.shutdown()
        server.server_close()

class ISockClientException(unittest.TestCase):
    def setUp(self):
        import threading

        try: self.server = isock.Server("localhost",4443)
        except isock.ServerException as error: self.fail("Init Error" + str(error))

        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def test_ISockClientException(self):
        client = isock.Client("localhost",4443)

        with self.assertRaises(isock.ServerException):
            received_data = client.runAction(_echo)

class ISockClientRetry(unittest.TestCase):
    def test_ISockClientRetry(self):
        client = isock.Client("localhost",4444)

        with self.assertRaises(isock.ClientException):
            received_data = client.runAction(_echo)

class ISockAction(unittest.TestCase):
    def setUp(self):
        import threading

        try: self.server = isock.Server("localhost",4445)
        except isock.ServerException as error: self.fail("Init Error" + str(error))

        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def test_ISockAction(self):
        client = isock.Client("localhost",4445)

        data_to_send = "dummy"

        with self.assertRaises(isock.ServerException):
            received_data = client.runAction(_echo,data_to_send)

        self.server.addAction(_echo())

        received_data = client.runAction(_echo,data_to_send)
        self.assertEqual(data_to_send,received_data)

class ISockActionException(unittest.TestCase):
    def setUp(self):
        import threading

        try: self.server = isock.Server("localhost",4446)
        except isock.ServerException as error: self.fail("Init Error" + str(error))

        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def test_ISockActionException(self):
        client = isock.Client("localhost",4446)

        data_to_send = "dummy"

        with self.assertRaises(isock.ClientException):
            received_data = client.runAction(_echo(),data_to_send)

        with self.assertRaises(isock.ClientException):
            received_data = client.runAction(None,data_to_send)

if __name__ == '__main__':
    unittest.main()