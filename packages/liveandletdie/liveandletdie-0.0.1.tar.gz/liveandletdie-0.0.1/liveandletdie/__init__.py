from datetime import datetime
import argparse
import os
import re
import signal
import socket
import subprocess
import sys
import urllib2


_VALID_HOST_PATTERN = r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}([:]\d+)?$'


def _log(enable_logging, message):
    if enable_logging:
        print('LIVEANDLETDIE: {}'.format(message))


def _validate_host(host):
    if re.match(_VALID_HOST_PATTERN, host):
        return host
    else:
        raise argparse.ArgumentTypeError('{} is not a valid host!'.format(host))


def split_host(host):
    """
    Splits host into host and port.
    
    :param str host:
        Host including port.
    
    :returns:
        A ``(str(host), int(port))`` tuple.
    """
    
    host, port = (host.split(':') + [None])[:2]
    return host, int(port)


def parse_args(enable_logging=False):
    """
    Parses command line arguments.
    
    Looks for --liveandletdie [host]
    
    :returns:
        A ``(str(host), int(port))`` or ``(None, None)`` tuple.
    """
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--liveandletdie',
                        help='Run as test live server.',
                        type=_validate_host,
                        nargs='?',
                        const='170.0.0.1:5000')
    args = parser.parse_args()
        
    if args.liveandletdie:
        _log(enable_logging, 'Running as test live server at {}'.format(args.liveandletdie))
        return split_host(args.liveandletdie)
    else:
        return (None, None)


def check(server):
    """Checks whether a server is running."""
    
    return server.check()


def live(app):
    """Starts a live app in a separate process and checks whether it is running."""
    return app.live()


def start(*args, **kwargs):
    """Alias for :funct:`live`"""
    live(*args, **kwargs)


def die(app):
    """Starts a live app in a separate process and checks whether it is running."""
    return app.live()


def stop(*args, **kwargs):
    """Alias for :funct:`die`"""
    die(*args, **kwargs)


def port_in_use(port, kill=False, enable_logging=False):
    """
    Checks whether a port is free or not.
    
    :param int port:
        The port number to check for.
        
    :param bool kill:
        If ``True`` the process will be killed.
    
    :returns:
        The process id as :class:`int` if in use, otherwise ``False`` .
    """
    
    process = subprocess.Popen('lsof -i :{}'.format(port).split(),
                               stdout=subprocess.PIPE)
    headers = process.stdout.readline().split()
    
    if not 'PID' in headers:
        _log(enable_logging, 'Port {} is free.'.format(port))
        return False
    
    index_pid = headers.index('PID')
    index_cmd = headers.index('COMMAND')
    
    row = process.stdout.readline().split()
    if len(row) < index_pid:
        return False
    
    pid = int(row[index_pid])
    command = row[index_cmd]
    
    if pid and command == 'python':
        _log(enable_logging,
            'Port {} is already being used by process {}!'.format(port, pid))
    
        if kill:
            _log(enable_logging,
                'Killing process with id {} listening on port {}!'
                    .format(pid, port))
            os.kill(pid, signal.SIGKILL)
            
            # Check whether it was really killed.
            try:
                # If still alive
                kill_process(pid, enable_logging)
                # call me again
                _log(enable_logging,
                    'Process {} is still alive! checking again...'.format(pid))
                return port_in_use(port, kill)
            except OSError:
                # If killed
                return False
        else:
            return pid


def kill_process(pid, enable_logging=False):
    try:
        _log(enable_logging, 'Killing process with id {}!'.format(pid))
        os.kill(int(pid), signal.SIGKILL)
        return 
    except OSError:
        # If killed
        return False


class Base(object):
    """
    Base class for all frameworks.
    
    :param str path:
        Absolute path to app directory or module (depends on framework).
        
    :param str host:
        A host at which the live server should listen.
        
    :param float timeout:
        Timeout in seconds for the check.
    
    :url:
        URL where to check whether the server is running.
        Default is "http://{host}".
    """
    
    def __init__(self, path, host='127.0.0.1', port=8001, timeout=10.0,
                 url=None, executable='python', enable_logging=False, suppress_output=True,
                 kill_orphans=False):
        
        self.path = path
        self.timeout = timeout
        self.url = url or 'http://{}:{}'.format(host, port)
        self.host = host
        self.port = port
        self.process = None
        self.executable = executable
        self.enable_logging = enable_logging
        self.suppress_output = suppress_output
        self.kill_orphans = kill_orphans
    
    
    def check(self):
        """Checks whether a server is running."""
        
        response = None
        sleeped = 0.0
        
        t = datetime.now()
        
        while not response:
            try:
                response = urllib2.urlopen(self.url)
            except urllib2.URLError:
                if sleeped > self.timeout:
                    raise Exception('{} server {} didn\'t start in specified timeout {} seconds!'\
                                        .format(self.__class__.__name__,
                                                self.url,
                                                self.timeout))
                sleeped = (datetime.now() - t).total_seconds()
        
        return (datetime.now() - t).total_seconds()
    
    
    def live(self, kill=False):
        """
        Starts a live server in a separate process
        and checks whether it is running.
        """
        
        pid = port_in_use(self.port, kill)
        
        if pid:
            raise Exception('Port {} is already being used by process {}!'
                                .format(self.port, pid))
        
        host = str(self.host)
        if re.match(_VALID_HOST_PATTERN, host):
            if self.suppress_output:
                with open(os.devnull, "w") as output:
                    self.process = subprocess.Popen(self.create_command(),
                        stdout=output, stderr=output)
            else:
                self.process = subprocess.Popen(self.create_command())

            _log(self.enable_logging, 'Starting process PID: {}'
                    .format(self.process.pid))
            duration = self.check()
            _log(self.enable_logging,
                 'Live server started in {} seconds. PID: {}'
                 .format(duration, self.process.pid))
            return self.process
        else:
            raise Exception('{} is not a valid host!'.format(host))
    
    
    def start(self, *args, **kwargs):
        """Alias for :meth:`.live`"""
        self.live(*args, **kwargs)


    def die(self):
        """Stops the server if it is running."""

        _log(self.enable_logging,
            'Stopping {} server with PID: {} running at {}.'
                .format(self.__class__.__name__,
                        self.process.pid,
                        self.url))
        
        if self.process:
            self.process.kill()
            self.process.wait()

        if self.kill_orphans:
            self._kill_orphans()


    def stop(self, *args, **kwargs):
        """Alias for :meth:`.die`"""
        self.die(*args, **kwargs)


    def _kill_orphans(self):
        pass


class WrapperBase(Base):
    """Base class for frameworks that require their app to be wrapped."""
    
    def create_command(self):
        return [
            self.executable,
            self.path,
            '--liveandletdie',
            '{}:{}'.format(self.host, self.port),
        ]


class Flask(WrapperBase):
    
    @staticmethod
    def wrap(app):
        """
        Adds test live server capability to a Flask app module.
        
        :param app:
            A :class:`flask.Flask` app instance.
        """
        
        host, port = parse_args()
        if host:
            app.config['DEBUG'] = False
            app.run(host=host, port=port)
            
            _log(self.enable_logging,
                 'Flask live server running at {}:{} terminated!'
                    .format(host, port))
            sys.exit()
    

class GAE(Base):
    """
    
    The first argument must be the path to dev_appserver.py.
    """
    
    def __init__(self, dev_appserver_path, *args, **kwargs):
        super(GAE, self).__init__(*args, **kwargs)
        self.dev_appserver_path = dev_appserver_path
        self.admin_port = kwargs.get('admin_port', 5555)
    
    def create_command(self):
        return [
            self.executable,
            self.dev_appserver_path,
            '--host={}'.format(self.host),
            '--port={}'.format(self.port),
            '--admin_port={}'.format(self.admin_port),
            self.path
        ]

    def _kill_orphans(self):
        process = subprocess.Popen('ps', stdout=subprocess.PIPE)
        headers = process.stdout.readline()
        
        _log(self.enable_logging, 'Killing orphaned GAE processes:')

        for row in process.stdout:
            if '_python_runtime.py' in row:
                pid = row.split()[0]
                kill_process(pid, self.enable_logging)


class WsgirefSimpleServer(WrapperBase):
    
    @staticmethod
    def wrap(app):
        host, port = parse_args()
        if host:            
            from wsgiref.simple_server import make_server
            
            s = make_server(host, port, app)
            s.serve_forever()
            s.server_close()
            
            _log(self.enable_logging,
                'wsgiref.simple_server running at {}:{} terminated!'
                    .format(host, port))
            sys.exit()
    

class Django(Base):
    def create_command(self):
        return [
            self.executable,
            os.path.join(self.path, 'manage.py'),
            'runserver',
            '{}:{}'.format(self.host, self.port),
        ]
