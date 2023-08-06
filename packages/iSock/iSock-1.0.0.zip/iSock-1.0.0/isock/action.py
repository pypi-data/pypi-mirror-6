import base

################################################################################
################################### Classes ####################################
################################################################################
class ActionException(base.ISockBaseException): pass

class Action(object):
    def action(self,data):
        raise ActionException("Not implemented!")
