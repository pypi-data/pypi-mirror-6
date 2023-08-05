import ast
import re

from cocaine import concurrent
from cocaine.concurrent import return_
from cocaine.services import Service
from cocaine.services.exceptions import ServiceError
from cocaine.tools.error import ServiceCallError

__author__ = 'Evgeny Safronov <division494@gmail.com>'


class Node(object):
    def __init__(self, node=None):
        self.node = node

    def execute(self):
        raise NotImplementedError()


class NodeInfo(Node):
    def __init__(self, node, locator):
        super(NodeInfo, self).__init__(node)
        self.locator = locator

    @concurrent.engine
    def execute(self):
        appNames = yield self.node.list()
        appInfoList = {}
        for appName in appNames:
            info = ''
            try:
                app = Service(appName)
                yield app.connect_through_locator(self.locator)
                info = yield app.info()
            except Exception as err:
                info = str(err)
            finally:
                appInfoList[appName] = info
        result = {
            'apps': appInfoList
        }
        return_(result)


class Call(object):
    def __init__(self, command, host='localhost', port=10053):
        if not command:
            raise ValueError('Please specify service name for getting API or full command to invoke')
        self.host = host
        self.port = port
        self.serviceName, separator, methodWithArguments = command.partition('.')
        rx = re.compile(r'(.*?)\((.*)\)')
        match = rx.match(methodWithArguments)
        if match:
            self.methodName, self.args = match.groups()
        else:
            self.methodName = methodWithArguments

    @concurrent.engine
    def execute(self):
        service = self.getService()
        yield service.connect(self.host, self.port)
        response = {
            'service': self.serviceName,
        }
        if not self.methodName:
            api = service.api
            response['request'] = 'api'
            response['response'] = api
        else:
            method = self.getMethod(service)
            args = self.parseArguments()
            result = yield method(*args)
            response['request'] = 'invoke'
            response['response'] = result
        return_(response)

    def getService(self):
        try:
            service = Service(self.serviceName)
            return service
        except Exception as err:
            raise ServiceCallError(self.serviceName, err)

    def getMethod(self, service):
        try:
            method = service.__getattribute__(self.methodName)
            return method
        except AttributeError:
            raise ServiceError(1, 'method "{0}" is not found'.format(self.methodName))

    def parseArguments(self):
        if not self.args:
            return ()

        try:
            args = ast.literal_eval(self.args)
            if not isinstance(args, tuple):
                args = (args,)
            return args
        except (SyntaxError, ValueError) as err:
            raise ServiceCallError(self.serviceName, err)
        except Exception as err:
            print(err, type(err))
