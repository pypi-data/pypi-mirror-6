# encoding: utf-8
'''
Created on 11 oct. 2012

@author: guillaume
'''

from yaml import load, Loader
import os


class Configuration(object):

    logger = ''
    initialized = False
    settings = {}
    ok = ''
    client_settings = {}
    client_initialized = False
    worker_settings = {}
    worker_initialized = False
    broker_settings = {}
    broker_initialized = False

    @staticmethod
    def _initconf(confpath=None):
        f = None
        if not(Configuration.initialized):
            if confpath is not None:
                try:
                    print "Configuration Loaded from:", confpath
                    f = open(confpath, 'r')
                    Configuration.settings = load(f, Loader=Loader)
                    Configuration.initialized = True
                finally:
                    if f is not None:
                        f.close()
            else:
                try:
                    confpath = Configuration.getConfigPath(__file__)
                    print "Configuration Loaded from:", confpath
                    f = open(confpath, 'r')
                    Configuration.settings = load(f, Loader=Loader)
                    Configuration.initialized = True
                finally:
                    if f is not None:
                        f.close()

    def __init__(self, confpath=None):
        '''
        Constructor
        '''
        self._initconf(confpath)
        self.settings = Configuration.settings
        self.initialized = True

    @staticmethod
    def updateclient(zooconf):
        Configuration.client_settings.update(zooconf)

    @staticmethod
    def getclient():
        '''
        return settings dictionnary
        '''
        if not Configuration.client_initialized:
            Configuration._initconf()
            Configuration.client_settings = Configuration.settings['client']
            Configuration.client_initialized = True
        return Configuration.client_settings

    @staticmethod
    def updateworker(zooconf):
        Configuration.worker_settings.update(zooconf)

    @staticmethod
    def getworker():
        '''
        return settings dictionnary
        '''
        if not Configuration.worker_initialized:
            Configuration._initconf()
            Configuration.worker_settings = Configuration.settings['worker']
            Configuration.worker_initialized = True
        return Configuration.worker_settings

    @staticmethod
    def updatebroker(zooconf):
        Configuration.broker_settings.update(zooconf)

    @staticmethod
    def getbroker():
        '''
        return settings dictionnary
        '''
        if not Configuration.broker_initialized:
            Configuration._initconf()
            Configuration.broker_settings = Configuration.settings['broker']
            Configuration.broker_initialized = True
        return Configuration.broker_settings

    @staticmethod
    def getInit():
        return Configuration.initialized

    @staticmethod
    def getLogger():
        return Configuration.logger

    @staticmethod
    def getClientMockMode():
        return Configuration.getclient()['mockmode']

    @staticmethod
    def getConfigPath(underscored_file):
        pathelements = underscored_file.split("/")
        index = pathelements.index("src")
        basepath = pathelements[:index]
        res = "/"
        for e in basepath:
            res = os.path.join(res, e)
        confpath = os.path.join(
            res, 'ressources/commons/conf/configuration.yaml')
        return confpath
