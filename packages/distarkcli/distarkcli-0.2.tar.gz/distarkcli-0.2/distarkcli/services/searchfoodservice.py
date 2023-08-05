#encoding: utf-8
'''
Created on 25 avr. 2013

@author: guillaume
'''
from distarkcli.protos.generic_service_pb2 import SEARCH_FOOD_REQUEST
from distarkcli.protos.generic_service_pb2 import SEARCH_FOOD_RESPONSE
from distarkcli.transport.distarkclient import Distarkcli
from distarkcli.utils.MyConfiguration import Configuration


def SearchFoodServiceFactory(request):
    factory = {}
    factory['REAL'] = SearchFoodService
    factory['MOCK'] = SearchFoodServiceMock
    clientmockmode = Configuration.getClientMockMode()
    return factory[clientmockmode](request)

class SearchFoodRequest():

    __req_str = ''

    def getReq(self):
        return self.__req_str

    def setReq(self, value):
        self.__req_str = value

    #IN: OneRequest
    def fillinPBOneRequest(self, pbonereq):
        pbonereq.rtype = SEARCH_FOOD_REQUEST
        pbonereq.searchfoodreq.request_food_str = self.__req_str

class Unit:
    UNIT_UNKNOWN = 0
    UNIT_GR = 1
    UNIT_PART = 2
    UNIT_POT = 3
    UNIT_UNITY = 4
    UNIT_SLICE = 5
    UNIT_ML = 6
    UNIT_CAN = 7
    UNIT_COFFEE_SPOON = 8

    @staticmethod
    def convert(pbunit):
        return Unit.UNIT_UNKNOWN

class Food():

    id = ''
    name = ''
    cal = 0.0
    glu = 0.0
    pro = 0.0
    lip = 0.0
    qty = 0.0
    qty_unit = Unit.UNIT_UNKNOWN


    def __init__(self, pbfood,
            id=None,
            name=None,
            cal=None,
            glu=None,
            pro=None,
            lip=None,
            qty=None,
            qty_unit=None):

        #build from a pbfood object
        if pbfood:
            self.id = pbfood.id
            self.name = pbfood.name
            self.cal = pbfood.cal
            self.glu = pbfood.glu
            self.pro = pbfood.pro
            self.lip = pbfood.lip
            self.qty = pbfood.qty
            self.qty_unit = Unit.convert(pbfood.qty_unit)
        else:
            #build by hand
            self.id = id
            self.name = name
            self.cal = cal
            self.glu = glu
            self.pro = pro
            self.lip = lip
            self.qty = qty
            self.qty_unit = qty_unit


class SearchFoodResponse():

    __foods = []


    #IN: OneResponse
    def __init__(self, pboneresponse=None):
        if pboneresponse:
            if pboneresponse.rtype == SEARCH_FOOD_RESPONSE:
                for f in pboneresponse.searchfoodresp.foods:
                    self.__foods.append(Food(f))
            else:
                raise Exception('Wrong response Type received !')

    def getFoods(self):
        return self.__foods

    def setFoods(self, value):
        self.__foods = value


class SearchFoodServiceMock():

    pbresptype = SEARCH_FOOD_RESPONSE

    def __init__(self, request):
        self.req = request

    def getResponse(self):

        resp = SearchFoodResponse()
        foods = []
        foods.append(Food(None, 1, 'saumon', 0.1, 0.2, 0.3, 0.4, 1, Unit.UNIT_UNITY))
        foods.append(Food(None, 2, 'foie gras', 0.1, 0.2, 0.3, 0.4, 1, Unit.UNIT_UNITY))
        foods.append(Food(None, 23, 'champagne', 0.1, 0.2, 0.3, 0.4, 1, Unit.UNIT_UNITY))
        foods.append(Food(None, 24, 'truffes au chocolat', 0.1, 0.2, 0.3, 0.4, 1, Unit.UNIT_UNITY))
        resp.setFoods(foods)
        return [self.pbresptype, resp]


class SearchFoodService(Distarkcli):
    '''
    Objectif: faire la requete à la construction
    la classe vit sa vie
    getReply renvoie la reponse si elle est arrivée
    '''

    pbresptype = SEARCH_FOOD_RESPONSE
    serviceName = 'SearchFoodService'
    pbrespHandler = SearchFoodResponse

    def __init__(self, searchfoodrequest):
        self.objreq = searchfoodrequest
        self.send()
