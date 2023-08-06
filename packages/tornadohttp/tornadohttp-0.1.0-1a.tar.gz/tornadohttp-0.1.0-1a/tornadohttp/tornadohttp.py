#!/usr/bin/env python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# Author: "Chris Ward <cward@redhat.com>

'''
tornadopy.tornadohttp
~~~~~~~~~~~~~~~~~~~~~

Generic, re-usable Tornado server and config classes.

Supports log handling, server startup / shutdown and
configuration loading.
'''

import logging
from functools import partial
import os
import signal
import sys
import time
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application

logging.basicConfig()
logger = logging.getLogger()


class TornadoHTTP(object):
    ''' HTTP (Tornado >=3.0) implemntation of MetriqueServer '''
    parent_pid = None
    child_pid = None
    handlers = []
    name = 'tornado'

    def __init__(self, **kwargs):
        config = {
            'api_docs': '',
            'autoreload': False,
            'cookie_secret': '__SECRET_SHHHHHH__',
            'debug': True,
            'gzip': True,
            'host': '127.0.0.1',
            'logdir': '',
            'logstdout': True,
            'log2file': False,
            'logfile': 'tornado.log',
            'log_keep': 3,
            'log_rotate': False,
            'log_rotate_bytes': 134217728,  # 128M 'maxBytes' before rotate
            'log_requests_file': 'tornado_access.log',
            'log_requests_name': 'access',
            'login_url': '/login',
            'pid_dir': '',
            'pid_name': 'tornado',
            'port': 8080,
            'ssl': False,
            'ssl_certificate': '',
            'ssl_certificate_key': '',
            'static_path': '',
            'template_path': '',
            'xsrf_cookies': False,
        }
        config.update(kwargs)
        self.config = config
        self.setup_logger()

    def _log_file_handler(self, logfile=None):
        logdir = os.path.expanduser(self.config.get('logdir'))
        logfile = logfile or self.config.get('logfile')
        logfile = os.path.join(logdir, logfile)
        rotate = self.config.get('log_rotate')
        rotate_bytes = self.config.get('log_rotate_bytes')
        rotate_keep = self.config.get('log_keep')

        if rotate:
            hdlr = logging.handlers.RotatingFileHandler(
                logfile, backupCount=rotate_keep, maxBytes=rotate_bytes)
        else:
            hdlr = logging.FileHandler(logfile)
        return hdlr

    def _debug_set_level(self, logger, level):
        if level in [-1, False]:
            logger.setLevel(logging.WARN)
        elif level in [0, None]:
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.DEBUG)
        return logger

    def setup_logger(self):
        '''Setup application logging

        The following loggers will be available:
            * logger - main

        By default, .debug, .info, .warn, etc methods are available in
        the main logger.

        Additionally, the following methods are also available via .logger:
            * logger.request_logger

        The base logger name is the value of the class attribute `name`.
        '''
        level = self.config.get('debug')
        logstdout = self.config.get('logstdout')
        logfile = self.config.get('logfile')
        log_format = "%(name)s.%(process)s:%(asctime)s:%(message)s"
        log_format = logging.Formatter(log_format, "%Y%m%dT%H%M%S")

        logger = logging.getLogger()
        logger.handlers = []
        if logstdout:
            hdlr = logging.StreamHandler()
            hdlr.setFormatter(log_format)
            logger.addHandler(hdlr)
        if self.config.get('log2file') and logfile:
            hdlr = self._log_file_handler()
            hdlr.setFormatter(log_format)
            logger.addHandler(hdlr)
        self._debug_set_level(logger, level)

        # prepare 'request' logger for storing request details
        r_logfile = self.config.get('log_requests_file')
        logger = logging.getLogger(self.config.get('log_requests_name'))
        hdlr = self._log_file_handler(logfile=r_logfile)
        logger.addHandler(hdlr)
        logger.propagate = 0
        logger.setLevel(logging.ERROR)

    @property
    def pid(self):
        '''Wrapper for os.getpid()'''
        return os.getpid()

    @property
    def pid_file(self):
        '''Return back the name of the current instance's pid file on disk'''
        pid_file = '%s.%s.pid' % (self.config.get('pid_name'), str(self.pid))
        path = os.path.join(self.config.get('pid_dir'), pid_file)
        return os.path.expanduser(path)

    def _prepare_web_app(self):
        ''' Config and Views'''
        logger.debug("tornado web app setup")

        self._web_app = Application(
            gzip=self.config.get('gzip'),
            debug=self.config.get('debug'),
            static_path=self.config.get('static_path'),
            handlers=self.handlers,
            cookie_secret=self.config.get('cookie_secret'),
            login_url=self.config.get('login_url'),
            xsrf_cookies=self.config.get('xsrf_cookies'),
            template_path=self.config.get('template_path'),
        )

        if self.config.get('debug') and not self.config.get('autoreload'):
            # FIXME hack to disable autoreload when debug is True
            from tornado import autoreload
            autoreload._reload_attempted = True
            autoreload._reload = lambda: None

        if self.config.get('ssl'):
            ssl_options = dict(
                certfile=os.path.expanduser(self.config.get('ssl_certificate')),
                keyfile=os.path.expanduser(self.config.get('ssl_certificate_key')))
            self.server = HTTPServer(self._web_app, ssl_options=ssl_options)
        else:
            self.server = HTTPServer(self._web_app)

    def set_pid(self):
        '''Store the current instances pid number into a pid file on disk'''
        if os.path.exists(self.pid_file):
            raise RuntimeError(
                "pid (%s) found in (%s)" % (self.pid,
                                            self.pid_file))
        else:
            with open(self.pid_file, 'w') as _file:
                _file.write(str(self.pid))
        signal.signal(signal.SIGTERM, self._inst_terminate_handler)
        signal.signal(signal.SIGINT, self._inst_kill_handler)
        logger.debug("PID stored (%s)" % self.pid)

    def remove_pid(self, quiet=False):
        '''Remove existing pid file on disk, if available'''
        error = None
        try:
            os.remove(self.pid_file)
        except OSError as error:
            if not quiet:
                logger.error(
                    'pid file not removed (%s); %s' % (self.pid_file, error))
        else:
            if not quiet:
                logger.debug("removed PID file: %s" % self.pid_file)

    def _init_basic_server(self):
        logger.debug('======= %s =======' % self.name)
        logger.debug(' Conf: %s' % self.config.get('config_file'))
        logger.debug(' Host: %s' % self.uri)
        logger.debug('  SSL: %s' % self.config.get('ssl'))

        host, port = self.config.get('host'), self.config.get('port')
        try:
            self.server.listen(port=port, address=host)
        except Exception as e:
            logger.error(
                'Failed to connect to %s:%s (%s)' % (host, port, e))
        try:
            IOLoop.instance().start()
        finally:
            self.remove_pid(quiet=True)

    def spawn_instance(self):
        '''Spawn a new tornado server instance'''
        logger.debug("spawning tornado %s..." % self.uri)
        self.set_pid()
        self._init_basic_server()

    @property
    def uri(self):
        '''Return a uri connection string for the current tornado instance'''
        host = self.config.get('host')
        ssl = self.config.get('ssl')
        port = self.config.get('port')
        uri = 'https://%s' % host if ssl else 'http://%s' % host
        uri += ':%s' % port
        return uri

    def start(self, fork=False):
        ''' Start a new tornado web app '''
        self._prepare_web_app()
        if fork:
            pid = os.fork()
            if pid == 0:
                self.spawn_instance()
        else:
            pid = self.pid
            self.spawn_instance()
        return pid

    def stop(self, delay=None):
        ''' Stop a running tornado web app '''
        if self.child_pid:
            os.kill(self.child_pid, signal.SIGTERM)
        else:
            self.server.stop()  # stop this tornado instance
            delayed_kill = partial(self._inst_delayed_stop, delay)
            IOLoop.instance().add_callback(delayed_kill)
        sys.exit(2)

    def _inst_stop(self, sig, delay=None):
        if self.child_pid:
            os.kill(self.child_pid, sig)
        else:
            self.stop(delay=delay)
        self.remove_pid(quiet=True)

    def _inst_terminate_handler(self, sig, frame):
        logger.debug("[INST] (%s) recieved KILL (9) signal" % self.pid)
        self._inst_stop(sig, 0)

    def _inst_kill_handler(self, sig, frame):
        logger.debug("[INST] (%s) recieved TERM (15) signal" % self.pid)
        self._inst_stop(sig)

    def _inst_delayed_stop(self, delay=None):
        if delay is None:
            if self.config.get('debug'):
                delay = 0
            else:
                delay = 5
        logger.debug("stop ioloop called (%s)... " % self.pid)
        TIMEOUT = float(delay) + time.time()
        logger.debug("Shutting down in T-%i seconds ..." % delay)
        IOLoop.instance().add_timeout(TIMEOUT, self._stop_ioloop)

    def _stop_ioloop(self):
        IOLoop.instance().stop()
        logger.debug("IOLoop stopped")
