import threading
from isock import Server
from isock import Client
from isock import Action

################################################################################
############################ Server actions ####################################
################################################################################
class Echo(Action):
    def action(self,data):
        return data

class Exec(Action):
    def __init__(self,exec_history):
        self.exec_history = exec_history

    def action(self,data):
        import subprocess
        self.exec_history.append(data)
        return subprocess.check_output(data,shell=True)

class ExecHistory(Action):
    def __init__(self,exec_history):
        self.exec_history = exec_history

    def action(self,data):
        return self.exec_history

class Time(Action):
    def action(self,data):
        import datetime
        return datetime.datetime.now()

################################################################################
############################ Server startup ####################################
################################################################################
history = []

server = Server("localhost",4440)
server.addAction(Echo())
server.addAction(Exec(history))
server.addAction(ExecHistory(history))
server.addAction(Time())
server_thread = threading.Thread(target=server.serve_forever)
server_thread.start()

################################################################################
############################ Client session ####################################
################################################################################

client = Client("localhost",4440)

print "############################# Echo test ################################"
print client.runAction(Echo,"Echo test!")

print "############################# Exec test ################################"
print client.runAction(Exec,"dir")
print client.runAction(Exec,"python -V")

print "############################# Exec history #############################"
print client.runAction(ExecHistory)

print "############################# Server time ##############################"
print client.runAction(Time)

################################################################################
############################ Server shutdown ###################################
################################################################################
server.shutdown()
server.server_close()
server_thread.join()
