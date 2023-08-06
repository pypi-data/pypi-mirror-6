from zope.interface import implements

from twisted.python import usage
from twisted.application.service import IServiceMaker
from twisted.plugin import IPlugin

from lisa.server import service

class Options(usage.Options):
    optParameters = [
        ['configuration', 'c', '/etc/lisa/server/configuration/lisa.json'],
        ['static', 's', '/tmp/lisa_static'],
        ['plugins', 'p', '/tmp/lisa_plugins'],
    ]

class ServiceMaker(object):
    implements(IServiceMaker, IPlugin)

    tapname = "lisa-server"
    description = "Lisa server."
    options=Options

    def makeService(self, config):
        return service.makeService(config)

serviceMaker = ServiceMaker()
