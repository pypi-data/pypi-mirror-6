#encoding: utf-8

import argparse
import traceback

from kazoo.client import KazooClient
from kazoo.client import KazooState
from kazoo.client import KeeperState
from distarkcli.utils.MyConfiguration import Configuration


class ZooConst(object):
    CLIENT='client'
    WORKER='worker'
    BROKER='broker'


def ZooBorgFactory(zoo_mock_mode, ip, port):
    factory = {}
    factory['REAL'] = ZooBorg
    factory['MOCK'] = ZooMock
    return factory[zoo_mock_mode](ip, port)


class ZooMock(object):

    ip = ''
    port = ''

    def __init__(self, ip, port):
        # copie de l'état lors de l'initialisation d'une nouvelle instance
        self.ip=ip
        self.port=port

    def getConf(self, conftype):
        '''
        conftype must be a Zooborg constant
        '''
        if conftype not in [ZooConst.CLIENT, ZooConst.WORKER, ZooConst.BROKER]:
            raise Exception('Zooborg.getConf: invalid type')

        zooconf={}

        #TODO: specialconf entries for the mock

        if conftype == ZooConst.CLIENT:
            zooconf['broker'] = {}
            zooconf['broker']['connectionstr'] = b"tcp://localhost:5555"

        elif conftype == ZooConst.BROKER:
            zooconf['bindstr']=b"tcp://*:5555"

        elif conftype == ZooConst.WORKER:
            zooconf['broker'] = {}
            zooconf['broker']['connectionstr'] = b"tcp://localhost:5555"

        else:
            raise Exception("ZooBorgconftype unknown")


        return zooconf

    def register(self, itemtype, item_id, handler):
        pass


class ZooBorg(object):
    '''
    distark
    distark/client/
    distark/client/conf
    distark/client/list/client_uniq_id (ephemeral?
    '''
    registred=[]
    client_settings={}
    client_initialized=False
    zk=KazooClient()
    ip=''
    port=''
    initialized=False
    __shared_state = {}  # variable de classe contenant l'état à partage

    @staticmethod
    def _my_listener(state):
        if state == KazooState.LOST:
            # Register somewhere that the session was lost
            print 'Zookeeper session listner: LOST'
        elif state == KazooState.SUSPENDED:
            # Handle being disconnected from Zookeeper
            print 'Zookeeper session listner: SUSPENDED'
        else:
            print 'Zookeeper session listner: (RE)CONNECTED'
            # Handle being connected/reconnected to Zookeeper

    def initconn(self):
        if not(self.initialized):
            self.connect()

            @self.zk.add_listener
            def watch_for_ro(state):
                if state == KazooState.CONNECTED:
                    if self.zk.client_state == KeeperState.CONNECTED_RO:
                        print("Read only mode!")
                    else:
                        print("Read/Write mode!")

    def __init__(self, ip, port):
        # copie de l'état lors de l'initialisation d'une nouvelle instance
        self.__dict__ = self.__shared_state
        self.ip=ip
        self.port=port
        self.initconn()

    def connect(self):
        self.zk = KazooClient(hosts=''.join([self.ip, ':', self.port]))
        print "ZOOKEEPER CONNECTED !!!"
        self.zk.start()
        self.zk.add_listener(self._my_listener)
        self.initialized=True

    def close(self):
        print "zoo connection closed"
        #traceback.print_exc()
        if (self.initialized):
            self.unregisterall()
            self.zk.stop()
            self.zk.close()
            self.initialized=False

    def unregisterall(self):
        for path in self.registred:
            if self.zk.exists(path):
                self.zk.delete(path, recursive=True)

    def register(self, itemtype, item_id, handler):
        '''
        register the item in zookeeper /list/
        itemtype must be a Zooborg constant
        item_id must be a string
        handler: method to call on conf change
        '''
        # Create a node with data
        #TODO: add system properties in data (ip, os)
        #TODO: add uniq client id
        if itemtype not in [ZooConst.CLIENT, ZooConst.WORKER, ZooConst.BROKER]:
            raise Exception('Zooborg.register: invalid type')
        self.initconn()
        self.zk.ensure_path("/distark/" + itemtype + "/list")
        path=''.join(['/distark/' + itemtype + '/list/', item_id])
        self.registred.append(path)
        data=b'ip̂,os'
        if not(self.zk.exists(path)):
            self.zk.create(path, data, None, True)
        else:
            self.zk.delete(path, recursive=True)
            self.zk.create(path, data, None, True)
        #reload conf if change in zoo
        self.zk.DataWatch('/distark/' + itemtype + '/conf/conf_reload_trigger',
                          handler)

    def unregister(self, itemtype, item_id):
        '''
        deregister the item in zookeeper /list/
        itemtype must be a Zooborg constant
        item_id must be a string
        '''
        if itemtype not in [ZooConst.CLIENT, ZooConst.WORKER, ZooConst.BROKER]:
            raise Exception('Zooborg.unregister: invalid type')
        self.initconn()
        self.zk.ensure_path("/distark/" + itemtype + "/list")
        path=''.join(['/distark/' + itemtype + '/list/', item_id])
        if self.zk.exists(path):
            self.zk.delete(path, recursive=True)

    def getList(self, listtype):
        '''
        listtype must be a Zooborg constant
        '''
        if listtype not in [ZooConst.CLIENT, ZooConst.WORKER, ZooConst.BROKER]:
            raise Exception('Zooborg.getList: invalid type')
        self.initconn()
        return self.zk.get_children('/distark/' + listtype + '/list')

    def _dumbdatawatcher(self, data, stat):
        print 'dumbwatcher'
        print 'data:', data
        print 'stat:', stat

    def _dumbchildrenwatcher(self, children):
        print 'dumbwatcher'
        print 'children:', children

    def getConf(self, conftype):
        '''
        conftype must be a Zooborg constant
        '''
        zooconf={}
        if conftype not in [ZooConst.CLIENT, ZooConst.WORKER, ZooConst.BROKER]:
            raise Exception('Zooborg.getConf: invalid type')

        self.initconn()
        if conftype in [ZooConst.CLIENT, ZooConst.WORKER]:
            zooconf={'broker': {'connectionstr': None}}
            zoopath='/distark/' + conftype + '/conf/broker/connectionstr'
            zooconf['broker']['connectionstr'], stat = self.zk.get(zoopath)

        if conftype in [ZooConst.BROKER]:
            zooconf={'bindstr': None}
            zoopath='/distark/' + conftype + '/conf/bindstr'
            zooconf['bindstr'], stat = self.zk.get(zoopath)

        return zooconf


def _initclientconf(zb):
    print "initclientconf"
    print "initclientconf: delete client root"
    if zb.zk.exists("/distark/client"):
        zb.zk.delete("/distark/client", recursive=True)
    print "initclientconf: create distark/client/list"
    zb.zk.ensure_path("/distark/client/list")
    print "initclientconf: create distark/client/conf"
    zb.zk.ensure_path("/distark/client/conf")
    print "initclientconf: create distark/client/broker/connectionstr"
    zb.zk.ensure_path("/distark/client/conf/broker/connectionstr")
    print "initclientconf: set data distark/client/broker/connectionstr"
    zb.zk.set("/distark/client/conf/broker/connectionstr",
              b"tcp://localhost:5555")
    zb.zk.ensure_path("/distark/client/conf/conf_reload_trigger")
    print "initclientconf: create distark/client/conf/conf_reload_trigger"


def _initworkerconf(zb):
    print "initworkerconf"
    print "initworkerconf: delete worker root"
    if zb.zk.exists("/distark/worker"):
        zb.zk.delete("/distark/worker", recursive=True)
    print "initworkerconf: create distark/worker/list"
    zb.zk.ensure_path("/distark/worker/list")
    print "initworkerconf: create distark/worker/conf"
    zb.zk.ensure_path("/distark/worker/conf")
    print "initworkerconf: create distark/worker/broker/connectionstr"
    zb.zk.ensure_path("/distark/worker/conf/broker/connectionstr")
    print "initworkerconf: set data distark/worker/broker/connectionstr"
    zb.zk.set("/distark/worker/conf/broker/connectionstr",
              b"tcp://localhost:5555")
    zb.zk.ensure_path("/distark/worker/conf/conf_reload_trigger")


def _initbrokerconf(zb):
    print "initbrokerconf"
    print "initbrokerconf: delete broker root"
    if zb.zk.exists("/distark/broker"):
        zb.zk.delete("/distark/broker", recursive=True)
    print "initbrokerconf: create distark/broker/list"
    zb.zk.ensure_path("/distark/broker/list")
    print "initbrokerconf: create distark/broker/conf"
    zb.zk.ensure_path("/distark/broker/conf")
    print "initbrokerconf: create distark/broker/bindstr"
    zb.zk.ensure_path("/distark/broker/conf/bindstr")
    print "initbrokerconf: set data distark/broker/bindstr"
    zb.zk.set("/distark/broker/conf/bindstr",
              b"tcp://*:5555")
    zb.zk.ensure_path("/distark/broker/conf/conf_reload_trigger")

if __name__ == '__main__':
    ##############################################
    #     ARGUMENTS PARSING
    ##############################################
    parser = argparse.ArgumentParser(description='Send requests')
    parser.add_argument('do',
                        help='test initclientconf initworkerconf initbrokerconf initall',
                        type=str)
    parser.set_defaults(do='test')
    args= parser.parse_args()
    print "Program Launched with args:" + str(args)
    print "Do:" + str(args.do)
    zb=None
    ip = Configuration.getclient()['zookeeper']['ip']
    port = Configuration.getclient()['zookeeper']['port']
    zb = ZooBorg(ip, port)
    try:
        if args.do == 'initclientconf':
            _initclientconf(zb)
        elif args.do == 'initworkerconf':
            _initworkerconf(zb)
        elif args.do == 'initbrokerconf':
            _initbrokerconf(zb)
        elif args.do == 'initall':
            _initworkerconf(zb)
            _initclientconf(zb)
            _initbrokerconf(zb)
        else:
            print 'do nothing !!!'

    except:
        traceback.print_exc()

    finally:
        #zb.unregisterclient('test_client')
        zb.close()
