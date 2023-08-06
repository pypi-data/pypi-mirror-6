#coding:utf8
'''
Created on 2014-2-24

@author: lan (www.9miao.com)
'''
from gfirefly.server.globalobject import GlobalObject,masterserviceHandle
from gtwisted.core import reactor
from gtwisted.utils import log

reactor = reactor


@masterserviceHandle
def serverStop():
    """
    """
    log.msg('stop')
    if GlobalObject().stophandler:
        GlobalObject().stophandler()
    reactor.callLater(0.5,reactor.stop)
    return True

@masterserviceHandle
def sreload():
    """
    """
    log.msg('reload')
    if GlobalObject().reloadmodule:
        reload(GlobalObject().reloadmodule)
    return True

@masterserviceHandle
def remote_connect(rname, rhost):
    """
    """
    GlobalObject().remote_connect(rname, rhost)

