#encoding: utf-8
'''
Created on 27 avr. 2013

@author: guillaume
'''


from distarkcli.protos.generic_service_pb2 import PBOneRequest
from distarkcli.protos.generic_service_pb2 import PBOneResponse
from distarkcli.protos.generic_service_pb2 import SIMPLE_RESPONSE
from distarkcli.protos.generic_service_pb2 import ERROR_NONE
from distarkcli.utils.PBUtils import PBUtils
from distarkcli.transport.majordomoclient import MajorDomoClient
from distarkcli.utils.MyConfiguration import Configuration
from distarkcli.utils.zoo import ZooBorg
from distarkcli.utils.uniq import Uniq


class ConnectionPoolBorg():

    __availableconnection = []
    __busyconnection = []
    initialized = False
    __shared_state = {}  # variable de classe contenant l'état à partage

    def _zconfchanged(self, data, stat):
        #print "pool: conf changed !"
        pass

    def __init__(self, maxconnection=10):
        # copie de l'état lors de l'initialisation d'une nouvelle instance
        self.__dict__ = self.__shared_state
        if not(self.initialized):
            #N MajorDomoClient
            #print "INIT ConnectionPool"
            zb = ZooBorg(Configuration.getclient()['zookeeper']['ip'],
                         Configuration.getclient()['zookeeper']['port'])
            zooconf = zb.getConf(ZooBorg.CLIENT)
            connection_str = zooconf['broker']['connectionstr']
            uniq = Uniq()
            for _ in range(1, maxconnection):
                conn = MajorDomoClient(connection_str, False, self)
                self.__availableconnection.append(conn)
                #register connexion
                zb.register(zb.CLIENT, uniq.getid(uniq.CLIENT), self._zconfchanged)
            self.initialized = True

    def getConnection(self):
        if len(self.__availableconnection) > 0:
            conn = self.__availableconnection.pop()
            self.__busyconnection.append(conn)
            #print 'added to busy',self.__busyconnection
            return conn
        else:
            raise Exception('ConnectionPool: No more connection available')

    def returnToPool(self, conn):
        #print self
        #make connection available
        if conn in self.__busyconnection:
            self.__availableconnection.append(conn)
            self.__busyconnection.remove(conn)
        else:
            raise Exception('ConnectionPool: ReturnToPool a non busy connection')

    def __str__(self):
        tuple = ("\nConnectionPool:\nAvailable connections:",
                 str(len(self.__availableconnection)),
                 "\nBusy connections:",
                 str(len(self.__busyconnection)))
        return ''.join(tuple)


class NaiveConnectionPool(object):
    __mdclient = None
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(NaiveConnectionPool, cls
                                  ).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        #One MajorDomoClient
        self.__mdclient = MajorDomoClient("tcp://localhost:5555", False, self)

    def getConnection(self):
        return self.__mdclient

    def returnToPool(self, conn):
        pass


class StubSimpleRequestConnectionPool():

    __oreq = None
    __oresp = None

    def getConnection(self):
        return self

    def __init__(self):
        pass

    def send(self, service, msg):
        if msg:
            self.__oreq = PBOneRequest()
            self.__oreq.ParseFromString(msg)
            PBUtils.dumpOneRequest(self.__oreq)

    def recv(self):
        self.__oresp = None
        if self.__oreq:
            self.__oresp = PBOneResponse()
            self.__oresp.rtype = SIMPLE_RESPONSE
            self.__oresp.etype = ERROR_NONE
            self.__oresp.gresp.computetime = 1.0
            self.__oresp.gresp.req.servicename = self.__oreq.greq.servicename
            self.__oresp.gresp.req.caller = self.__oreq.greq.caller
            self.__oresp.gresp.req.ipadress = self.__oreq.greq.ipadress
            self.__oresp.simpleresp.boum = ''.join(
                reversed(self.__oreq.simplereq.youpla))
            PBUtils.dumpOneResponse(self.__oresp)
            res = self.__oresp.SerializeToString()
            return res

    def close(self):
        print 'Connection closed'
        pass

    def returnToPool(self, conn):
        print 'Connection closed'
        pass
