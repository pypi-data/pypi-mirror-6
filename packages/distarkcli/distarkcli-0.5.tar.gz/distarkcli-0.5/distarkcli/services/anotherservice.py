#encoding: utf-8
'''
Created on 25 avr. 2013

@author: guillaume
'''
from distarkcli.protos.generic_service_pb2 import ANOTHER_REQUEST
from generic_service_pb2 import ANOTHER_RESPONSE
from distarkcli.transport.distarkclient import Distarkcli
from distarkcli.utils.MyConfiguration import Configuration


def AnotherServiceFactory(request):
    factory = {}
    factory['REAL'] = AnotherService
    factory['MOCK'] = AnotherServiceMock
    clientmockmode = Configuration.getClientMockMode()
    return factory[clientmockmode](request)


class AnotherRequest():

    __requeststr = ''

    def getRequestStr(self):
        return self.__requeststr

    def setRequestStr(self, value):
        self.__requeststr = value

    #IN: OneRequest
    def fillinPBOneRequest(self, pbonereq):
        pbonereq.rtype = ANOTHER_REQUEST
        pbonereq.anotherreq.request_str = self.__requeststr


class AnotherResponse():

    __responsestr = ''

    #IN: OneResponse
    def __init__(self, pboneresponse=None):
        if pboneresponse:
            if pboneresponse.rtype == ANOTHER_RESPONSE:
                self.__responsestr = pboneresponse.anotherresp.response_str
            else:
                raise Exception('Wrong response Type received !')

    def getResponseStr(self):
        return self.__responsestr

    def setResponseStr(self, value):
        self.__responsestr = value


class AnotherServiceMock():

    pbresptype = ANOTHER_RESPONSE

    def __init__(self, request):
        self.req = request

    def getResponse(self):

        resp = AnotherResponse()
        resp.setResponseStr(''.join([self.req.getRequestStr(), self.req.getRequestStr()]))
        return [self.pbresptype, resp]


class AnotherService(Distarkcli):
    '''
    Objectif: faire la requete à la construction
    la classe vit sa vie
    getReply renvoie la reponse si elle est arrivée
    '''

    pbresptype = ANOTHER_RESPONSE
    serviceName = 'AnotherService'
    pbrespHandler = AnotherResponse

    def __init__(self, anotherrequest):
        self.objreq = anotherrequest
        self.send()
