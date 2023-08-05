import collections
import logging
import os
import sys

from opster import Dispatcher

from cocaine.services import Locator, Service
from tornado.ioloop import IOLoop
from cocaine.tools.actions import proxy
from cocaine.tools.cli import Executor
from cocaine.tools.error import Error as ToolsError

__author__ = 'Evgeny Safronov <division494@gmail.com>'


DESCRIPTION = ''
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 10053


BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


COLORS = {
    'DEBUG': WHITE,
    'INFO': GREEN,
    'WARNING': YELLOW,
    'CRITICAL': YELLOW,
    'ERROR': RED
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, colored=True):
        logging.Formatter.__init__(self, msg)
        self.colored = colored

    def format(self, record):
        levelname = record.levelname
        if self.colored and levelname in COLORS:
            record.msg = COLOR_SEQ % (30 + COLORS[levelname]) + str(record.msg) + RESET_SEQ
        return logging.Formatter.format(self, record)


def interactiveEmit(self, record):
    # Monkey patch Emit function to avoid new lines between records
    try:
        if str(record.msg).endswith('... '):
            fs = '%s'
        else:
            fs = '%s\n'
        msg = self.format(record)
        stream = self.stream
        if not hasattr(logging, '_unicode') or not logging._unicode:  # if no unicode support...
            stream.write(fs % msg)
        else:
            try:
                if isinstance(msg, unicode) and getattr(stream, 'encoding', None):
                    ufs = fs.decode(stream.encoding)
                    try:
                        stream.write(ufs % msg)
                    except UnicodeEncodeError:
                        stream.write((ufs % msg).encode(stream.encoding))
                else:
                    stream.write(fs % msg)
            except UnicodeError:
                stream.write(fs % msg.encode("UTF-8"))
        self.flush()
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        self.handleError(record)


class Global(object):
    options = [
        ('h', 'host', DEFAULT_HOST, 'hostname'),
        ('p', 'port', DEFAULT_PORT, 'port'),
        ('', 'timeout', 1.0, 'timeout, s'),
        ('', 'color', True, 'enable colored output'),
        ('', 'debug', ('disable', 'tools', 'all'), 'enable debug mode'),
    ]

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, color=False, timeout=False, debug=False):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.executor = Executor(timeout)
        self._locator = None
        self.configureLog(debug=debug, color=color)

    @staticmethod
    def configureLog(debug='disable', color=True, logNames=None):
        if not logNames:
            logNames = ['cocaine.tools']
        message = '%(message)s'
        level = logging.INFO
        if debug != 'disable':
            message = '[%(asctime)s] %(name)s: %(levelname)-8s: %(message)s'
            level = logging.DEBUG

        ch = logging.StreamHandler()
        if debug == 'disable':
            setattr(logging.StreamHandler, logging.StreamHandler.emit.__name__, interactiveEmit)
        ch.fileno = ch.stream.fileno
        ch.setLevel(level)
        formatter = ColoredFormatter(message, colored=color and sys.stdin.isatty())
        ch.setFormatter(formatter)

        if debug == 'all':
            logNames.append('cocaine')

        for logName in logNames:
            log = logging.getLogger(logName)
            log.setLevel(logging.DEBUG)
            log.propagate = False
            log.addHandler(ch)

    def run_sync(self, func):
        result_future = [None]

        def handle_result(future):
            result_future[0] = future
            IOLoop.current().stop()

        df = func()
        df.add_callback(handle_result)
        IOLoop.current().start()
        result_future[0].get()

    @property
    def locator(self):
        if self._locator:
            return self._locator
        else:
            try:
                locator = Locator()
                self.run_sync(lambda: locator.connect(self.host, self.port, self.timeout))
                self._locator = locator
                return locator
            except Exception as err:
                raise ToolsError(err)

    def getService(self, name):
        try:
            service = Service(name)
            self.run_sync(lambda: service.connect_through_locator(self.locator, self.timeout))
            return service
        except Exception as err:
            raise ToolsError(err)


def middleware(func):
    def extract_dict(source, *keys):
        dest = {}
        for k in keys:
            dest[k] = source.pop(k, None)
        return dest

    def inner(*args, **kwargs):
        opts = extract_dict(kwargs, 'host', 'port', 'color', 'timeout', 'debug')
        if func.__name__ == 'help_inner':
            return func(*args, **kwargs)
        locator = Global(**opts)
        return func(locator, *args, **kwargs)
    return inner


d = Dispatcher(globaloptions=Global.options, middleware=middleware)


class dispatcher:
    app = Dispatcher(globaloptions=Global.options, middleware=middleware)
    profile = Dispatcher(globaloptions=Global.options, middleware=middleware)
    runlist = Dispatcher(globaloptions=Global.options, middleware=middleware)
    crashlog = Dispatcher(globaloptions=Global.options, middleware=middleware)
    group = Dispatcher(globaloptions=Global.options, middleware=middleware)
    proxy = Dispatcher()


@d.command()
def info(options):
    """Show information about cocaine runtime

    Return json-like string with information about cocaine-runtime.
    """
    options.executor.executeAction('info', **{
        'node': options.getService('node'),
        'locator': options.locator
    })


@d.command(usage='SERVICE [METHOD ["ARGS"]]')
def call(options,
         service, method='', args=''):
    """Invoke specified method from service.

    Performs method invocation from specified service. Service name should be correct string and must be correctly
    located through locator. By default, locator endpoint is `localhost, 10053`, but it can be changed by passing
    global `--host` and `--port` arguments.

    Method arguments should be passed in double quotes as they would be written in Python.
    If no method provided, service API will be printed.
    """
    command = '{0}.{1}({2})'.format(service, method, args)
    options.executor.executeAction('call', **{
        'command': command,
        'host': options.host,
        'port': options.port
    })


@dispatcher.app.command(name='list')
def app_list(options):
    """Show installed applications list."""
    options.executor.executeAction('app:list', **{
        'storage': options.getService('storage')
    })


@dispatcher.app.command(name='view', usage='--name=NAME')
def app_view(options,
             name=('n', '', 'application name')):
    """Show manifest context for application.

    If application is not uploaded, an error will be displayed.
    """
    options.executor.executeAction('app:view', **{
        'storage': options.getService('storage'),
        'name': name,
    })


@dispatcher.app.command(name='upload', usage='[PATH] [--name=NAME] [--manifest=MANIFEST] [--package=PACKAGE]')
def app_upload(options,
               path=None,
               name=('n', '', 'application name'),
               manifest=('', '', 'manifest file name'),
               package=('', '', 'path to the application archive'),
               docker_address=('', '', 'docker address'),
               registry=('', '', 'registry address'),
               recipe=('', '', 'path to the recipe file')):
    """Upload application with its environment (directory) into the storage.

    Application directory or its subdirectories must contain valid manifest file named `manifest.json` or `manifest`
    otherwise you must specify it explicitly by setting `--manifest` option.

    You can specify application name. By default, leaf directory name is treated as application name.

    If you have already prepared application archive (*.tar.gz), you can explicitly specify path to it by setting
    `--package` option.

    You can control process of creating and uploading application by specifying `--debug=tools` option. This is helpful
    when some errors occurred.
    """
    TIMEOUT_THRESHOLD = 120.0
    if options.executor.timeout < TIMEOUT_THRESHOLD:
        logging.getLogger('cocaine.tools').info('Setting timeout to the %fs', TIMEOUT_THRESHOLD)
        options.executor.timeout = TIMEOUT_THRESHOLD
    MutexRecord = collections.namedtuple('MutexRecord', 'value, name')
    mutex = [
        (MutexRecord(path, 'PATH'), MutexRecord(package, '--package')),
        (MutexRecord(package, '--package'), MutexRecord(docker_address, '--docker')),
        (MutexRecord(package, '--package'), MutexRecord(registry, '--registry')),
    ]
    for (f, s) in mutex:
        if f.value and s.value:
            print('Wrong usage: option {0} and {1} are mutual exclusive, you can only force one'.format(f.name, s.name))
            exit(os.EX_USAGE)

    if package:
        options.executor.executeAction('app:upload-manual', **{
            'storage': options.getService('storage'),
            'name': name,
            'manifest': manifest,
            'package': package
        })
    elif docker_address:
        options.executor.executeAction('app:upload-docker', **{
            'storage': options.getService('storage'),
            'path': path,
            'name': name,
            'manifest': manifest,
            'address': docker_address,
            'registry': registry
        })
    else:
        options.executor.executeAction('app:upload', **{
            'storage': options.getService('storage'),
            'path': path,
            'name': name,
            'manifest': manifest
        })


@dispatcher.app.command(name='remove')
def app_remove(options,
               name=('n', '', 'application name')):
    """Remove application from storage.

    No error messages will display if specified application is not uploaded.
    """
    options.executor.executeAction('app:remove', **{
        'storage': options.getService('storage'),
        'name': name
    })


@dispatcher.app.command(name='start')
def app_start(options,
              name=('n', '', 'application name'),
              profile=('r', '', 'profile name')):
    """Start application with specified profile.

    Does nothing if application is already running.
    """
    options.executor.executeAction('app:start', **{
        'node': options.getService('node'),
        'name': name,
        'profile': profile
    })


@dispatcher.app.command(name='pause')
def app_pause(options,
              name=('n', '', 'application name')):
    """Stop application.

    This command is alias for ```cocaine-tool app stop```.
    """
    options.executor.executeAction('app:pause', **{
        'node': options.getService('node'),
        'name': name
    })


@dispatcher.app.command(name='stop')
def app_stop(options,
             name=('n', '', 'application name')):
    """Stop application."""
    options.executor.executeAction('app:stop', **{
        'node': options.getService('node'),
        'name': name
    })


@dispatcher.app.command(name='restart')
def app_restart(options,
                name=('n', '', 'application name'),
                profile=('r', '', 'profile name')):
    """Restart application.

    Executes ```cocaine-tool app pause``` and ```cocaine-tool app start``` sequentially.

    It can be used to quickly change application profile.
    """
    options.executor.executeAction('app:restart', **{
        'node': options.getService('node'),
        'locator': options.locator,
        'name': name,
        'profile': profile
    })


@dispatcher.app.command()
def check(options,
          name=('n', '', 'application name')):
    """Checks application status."""
    options.executor.executeAction('app:check', **{
        'node': options.getService('node'),
        'storage': options.getService('storage'),
        'locator': options.locator,
        'name': name,
    })


@dispatcher.profile.command(name='list')
def profile_list(options):
    """Show installed profiles."""
    options.executor.executeAction('profile:list', **{
        'storage': options.getService('storage')
    })


@dispatcher.profile.command(name='view')
def profile_view(options,
                 name=('n', '', 'profile name')):
    """Show profile configuration context."""
    options.executor.executeAction('profile:view', **{
        'storage': options.getService('storage'),
        'name': name
    })


@dispatcher.profile.command(name='upload')
def profile_upload(options,
                   name=('n', '', 'profile name'),
                   profile=('', '', 'path to profile file')):
    """Upload profile into the storage."""
    options.executor.executeAction('profile:upload', **{
        'storage': options.getService('storage'),
        'name': name,
        'profile': profile
    })


@dispatcher.profile.command(name='remove')
def profile_remove(options,
                   name=('n', '', 'profile name')):
    """Remove profile from the storage."""
    options.executor.executeAction('profile:remove', **{
        'storage': options.getService('storage'),
        'name': name
    })


@dispatcher.runlist.command(name='list')
def runlist_list(options):
    """Show uploaded runlists."""
    options.executor.executeAction('runlist:list', **{
        'storage': options.getService('storage')
    })


@dispatcher.runlist.command(name='view')
def runlist_view(options,
                 name=('n', '', 'name')):
    """Show configuration context for runlist."""
    options.executor.executeAction('runlist:view', **{
        'storage': options.getService('storage'),
        'name': name
    })


@dispatcher.runlist.command(name='upload')
def runlist_upload(options,
                   name=('n', '', 'name'),
                   runlist=('', '', 'path to the runlist configuration json file')):
    """Upload runlist with context into the storage."""
    options.executor.executeAction('runlist:upload', **{
        'storage': options.getService('storage'),
        'name': name,
        'runlist': runlist
    })


@dispatcher.runlist.command(name='create')
def runlist_create(options,
                   name=('n', '', 'name')):
    """Create runlist and upload it into the storage."""
    options.executor.executeAction('runlist:create', **{
        'storage': options.getService('storage'),
        'name': name
    })


@dispatcher.runlist.command(name='remove')
def runlist_remove(options,
                   name=('n', '', 'name')):
    """Remove runlist from the storage."""
    options.executor.executeAction('runlist:remove', **{
        'storage': options.getService('storage'),
        'name': name
    })


@dispatcher.runlist.command(name='add-app')
def runlist_add_app(options,
                    name=('n', '', 'runlist name'),
                    app=('', '', 'application name'),
                    profile=('', '', 'suggested profile'),
                    force=('', False, 'create runlist if it is not exist')):
    """Add specified application with profile to the runlist.

    Existence of application or profile is not checked.
    """
    options.executor.executeAction('runlist:add-app', **{
        'storage': options.getService('storage'),
        'name': name,
        'app': app,
        'profile': profile,
        'force': force
    })


@dispatcher.crashlog.command(name='status')
def crashlog_status(options):
    """Show crashlog status.
    """
    options.executor.executeAction('crashlog:status', **{
        'storage': options.getService('storage'),
    })

@dispatcher.crashlog.command(name='list')
def crashlog_list(options,
                  name=('n', '', 'name')):
    """Show crashlogs list for application.

    Prints crashlog list in timestamp - uuid format.
    """
    options.executor.executeAction('crashlog:list', **{
        'storage': options.getService('storage'),
        'name': name
    })


@dispatcher.crashlog.command(name='view')
def crashlog_view(options,
                  name=('n', '', 'name'),
                  timestamp=('t', '', 'timestamp')):
    """Show crashlog for application with specified timestamp."""
    options.executor.executeAction('crashlog:view', **{
        'storage': options.getService('storage'),
        'name': name,
        'timestamp': timestamp
    })


@dispatcher.crashlog.command(name='remove')
def crashlog_remove(options,
                    name=('n', '', 'name'),
                    timestamp=('t', '', 'timestamp')):
    """Remove crashlog for application with specified timestamp from the storage."""
    options.executor.executeAction('crashlog:remove', **{
        'storage': options.getService('storage'),
        'name': name,
        'timestamp': timestamp
    })


@dispatcher.crashlog.command(name='removeall')
def crashlog_removeall(options,
                       name=('n', '', 'name')):
    """Remove all crashlogs for application from the storage."""
    options.executor.executeAction('crashlog:removeall', **{
        'storage': options.getService('storage'),
        'name': name,
    })


@dispatcher.group.command(name='list', usage='')
def group_list(options):
    """Show routing groups.
    """
    options.executor.executeAction('group:list', **{
        'storage': options.getService('storage')
    })


@dispatcher.group.command(name='view', usage='NAME')
def group_view(options,
               name):
    """Show specified routing group.
    """
    options.executor.executeAction('group:view', **{
        'storage': options.getService('storage'),
        'name': name
    })


@dispatcher.group.command(name='create', usage='NAME [CONTENT]')
def group_create(options,
                 name,
                 content=None):
    """Create routing group.

    You can optionally specify content for created routing group. It can be both direct json expression in single
    quotes, or path to the json file with settings. The settings itself must be key-value list, where `key` represents
    application name, and `value` represents its weight. For example:

    cocaine-tool group create new_group '{
        "app": 1,
        "another_app": 2
    }'.

    Warning: all application weights must be positive integers.
    """
    options.executor.executeAction('group:create', **{
        'storage': options.getService('storage'),
        'name': name,
        'content': content
    })


@dispatcher.group.command(name='remove', usage='NAME')
def group_remove(options,
                 name):
    """Remove routing group.
    """
    options.executor.executeAction('group:remove', **{
        'storage': options.getService('storage'),
        'name': name
    })


@dispatcher.group.command(name='refresh', usage='[NAME]')
def group_refresh(options,
                  name=None):
    """Refresh routing group.

    If group name is empty this command will refresh all groups.
    """
    options.executor.executeAction('group:refresh', **{
        'locator': options.locator,
        'storage': options.getService('storage'),
        'name': name
    })


@dispatcher.group.command(name='push', usage='NAME APP WEIGHT')
def group_push(options,
               name,
               app,
               weight):
    """Add application with its weight into the routing group.

    Warning: application weight must be positive integer.
    """
    options.executor.executeAction('group:app:add', **{
        'storage': options.getService('storage'),
        'name': name,
        'app': app,
        'weight': weight
    })


@dispatcher.group.command(name='pop', usage='NAME APP')
def group_pop(options,
              name,
              app):
    """Remove application from routing group.
    """
    options.executor.executeAction('group:app:remove', **{
        'storage': options.getService('storage'),
        'name': name,
        'app': app
    })


DEFAULT_COCAINE_PROXY_PID_FILE = '/var/run/cocaine-python-proxy.pid'


@dispatcher.proxy.command()
def start(port=('', 8080, 'server port'),
          count=('', 0, 'server subprocess count (0 means optimal for current CPU count)'),
          config=('', '/etc/cocaine/cocaine-tornado-proxy.conf', 'path to the configuration file'),
          daemon=('', False, 'run as daemon'),
          pidfile=('', DEFAULT_COCAINE_PROXY_PID_FILE, 'pidfile')):
    """Start embedded cocaine proxy.
    """
    Global.configureLog(logNames=['cocaine.tools', 'cocaine.proxy'])
    try:
        proxy.Start(**{
            'port': port,
            'daemon': daemon,
            'count': count,
            'config': config,
            'pidfile': pidfile,
        }).execute()
    except proxy.Error as err:
        logging.getLogger('cocaine.tools').error('Cocaine tool error - %s', err)


@dispatcher.proxy.command()
def stop(pidfile=('', DEFAULT_COCAINE_PROXY_PID_FILE, 'pidfile')):
    """Stop embedded cocaine proxy.
    """
    Global.configureLog(logNames=['cocaine.tools', 'cocaine.proxy'])
    try:
        proxy.Stop(**{
            'pidfile': pidfile,
        }).execute()
    except proxy.Error as err:
        logging.getLogger('cocaine.tools').error('Cocaine tool error - %s', err)


@dispatcher.proxy.command()
def status(pidfile=('', DEFAULT_COCAINE_PROXY_PID_FILE, 'pidfile')):
    """Show embedded cocaine proxy status.
    """
    Global.configureLog(logNames=['cocaine.tools', 'cocaine.proxy'])
    try:
        proxy.Status(**{
            'pidfile': pidfile,
        }).execute()
    except proxy.Error as err:
        logging.getLogger('cocaine.tools').error('Cocaine tool error - %s', err)


d.nest('app', dispatcher.app, 'application commands')
d.nest('profile', dispatcher.profile, 'profile commands')
d.nest('runlist', dispatcher.runlist, 'runlist commands')
d.nest('crashlog', dispatcher.crashlog, 'crashlog commands')
d.nest('group', dispatcher.group, 'routing group commands')
d.nest('proxy', dispatcher.proxy, 'cocaine proxy commands')
