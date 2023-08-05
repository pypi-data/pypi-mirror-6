#encoding: utf-8
'''
Created on 25 avr. 2013

@author: guillaume
'''
from distarkcli.protos.generic_service_pb2 import SIMPLE_REQUEST
from distarkcli.protos.generic_service_pb2 import SIMPLE_RESPONSE
from distarkcli.transport.distarkclient import Distarkcli
from distarkcli.utils.MyConfiguration import Configuration

def SimpleServiceFactory(request):
    factory = {}
    factory['REAL'] = SimpleService
    factory['MOCK'] = SimpleServiceMock
    clientmockmode = Configuration.getClientMockMode()
    return factory[clientmockmode](request)

class SimpleRequest():

    __youpla = ''

    def getYoupla(self):
        return self.__youpla

    def setYoupla(self, value):
        self.__youpla = value

    #IN: OneRequest
    def fillinPBOneRequest(self, pbonereq):
        pbonereq.rtype = SIMPLE_REQUEST
        pbonereq.simplereq.youpla = self.__youpla

    youpla = property(getYoupla, setYoupla, None, None)


class SimpleResponse():

    __boum = ''

    #IN: OneResponse
    def __init__(self, pboneresponse=None):
        #TODO: test rtype

        if pboneresponse:
            if pboneresponse.rtype == SIMPLE_RESPONSE:
                self.__boum = pboneresponse.simpleresp.boum
            else:
                raise Exception('Wrong response Type received !')

    def getBoum(self):
        return self.__boum

    def setBoum(self, value):
        self.__boum = value

    boum = property(getBoum, setBoum, None, None)

class SimpleServiceMock():

    pbresptype = SIMPLE_RESPONSE

    def __init__(self, simplerequest):
        self.objreq = simplerequest

    def getResponse(self):
        res = SimpleResponse()
        res.setBoum(''.join(reversed(self.objreq.getYoupla())))
        return [self.pbresptype, res]


class SimpleService(Distarkcli):
    '''
    Objectif: faire la requete à la construction
    la classe vit sa vie
    getReply renvoie la reponse si elle est arrivée
    '''

    pbresptype = SIMPLE_RESPONSE
    serviceName = 'SimpleService'
    pbrespHandler = SimpleResponse

    def __init__(self, simplerequest):
        self.objreq = simplerequest
        self.send()
