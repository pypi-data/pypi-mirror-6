#!/usr/bin/env python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# Author: "Chris Ward <cward@redhat.com>

import logging
from functools import partial
import os
import signal
import time
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application

# setup default root logger, but remove default StreamHandler (stderr)
# Handlers will be added upon __init__()
logging.basicConfig()
root_logger = logging.getLogger()
[root_logger.removeHandler(hdlr) for hdlr in root_logger.handlers]
BASIC_FORMAT = "%(name)s:%(asctime)s:%(message)s"
LOG_FORMAT = logging.Formatter(BASIC_FORMAT, "%Y%m%dT%H%M%S")


STATIC_PATH = 'static/'
LOGIN_URL = '/login'
COOKIE_SECRET = '__DEFAULT_COOKIE_SECRET__'
SSL_CERT = 'mydomain.crt'
SSL_KEY = 'mydomain.key'
PID_DIR = ''
LOG_DIR = ''
LOG_FILE = 'tornadod.log'


class TornadoHTTPServer(object):
    ''' HTTP (Tornado >=3.0) implemntation of MetriqueServer '''
    def __init__(self, config_file=None, **kwargs):
        self.parent_pid = None
        self.child_pid = None
        self.handlers = []

        conf = config_file or {}

        # key aliases (to shorten line <80c)
        cert = 'ssl_certificate'
        key = 'ssl_certificate_key'

        conf.host = kwargs.pop('host', '127.0.0.1')
        conf.port = kwargs.pop('port', '5420')
        conf.debug = kwargs.pop('debug', True)
        conf.gzip = kwargs.pop('gzip', True)
        conf.login_url = kwargs.pop('login_url', LOGIN_URL)
        conf.static_path = kwargs.pop('static_path', STATIC_PATH)
        conf.cookie_secret = kwargs.pop('cookie_secret', COOKIE_SECRET)
        conf.xsrf_cookies = kwargs.pop('xsrf_cookies', False)
        conf.autoreload = kwargs.pop('autoreload', True)
        conf.ssl = kwargs.pop('ssl', False)
        conf.ssl_certificate = kwargs.pop(cert, SSL_CERT)
        conf.ssl_certificate_key = kwargs.pop(key, SSL_KEY)
        conf.pid_dir = kwargs.pop('pid_dir', PID_DIR)
        conf.log_dir = kwargs.pop('log_dir', LOG_DIR)
        conf.logstdout = kwargs.pop('logstdout', True)
        conf.log2file = kwargs.pop('logstdout', False)
        conf.logfile = kwargs.pop('logfile', LOG_FILE)
        conf.logrotate = kwargs.pop('logrotate', False)
        conf.logkeep = kwargs.pop('logkeep', 3)
        conf.logger_propogate = kwargs.pop('logkeep', False)

        logger_name = kwargs.pop('logger_name', __name__)
        conf.logger_name = '%s.%s' % (logger_name, self.pid)

        # update config with additional non-default kwargs
        for k, v in kwargs.items():
            conf[k] = v

        self.conf = conf

        self.debug_set()

    def debug_set(self):
        logdir = os.path.expanduser(self.logdir)
        logfile = os.path.join(logdir, self.logfile)

        if self.debug == 2:
            logger = logging.getLogger()
            logger.propagate = self.logger_propogate
        else:
            logger = logging.getLogger(self.logger_name)
            logger.propagate = self.logger_propogate

        # handlers are removed on module load
        #logger.handlers = []  # reset handlers

        if self.logstdout:
            hdlr = logging.StreamHandler()
            hdlr.setFormatter(LOG_FORMAT)
            logger.addHandler(hdlr)

        if self.log2file and logfile:
            if self.logrotate:
                hdlr = logging.handlers.RotatingFileHandler(
                    logfile, backupCount=self.logkeep, maxBytes=self.logrotate)
            else:
                hdlr = logging.FileHandler(logfile)
            hdlr.setFormatter(LOG_FORMAT)
            logger.addHandler(hdlr)

        if self.debug in [-1, False]:
            logger.setLevel(logging.WARN)
        elif self.debug in [0, None]:
            logger.setLevel(logging.INFO)
        elif self.debug in [True, 1, 2]:
            logger.setLevel(logging.DEBUG)
        self.logger = logger

    @property
    def pid(self):
        return os.getpid()

    @property
    def pid_file(self):
        pid_file = 'metriqued.%s.pid' % str(self.pid)
        path = os.path.join(self.mconf['piddir'], pid_file)
        return os.path.expanduser(path)

    def _prepare_web_app(self):
        ''' Config and Views'''
        self.logger.debug("tornado web app setup")

        self._web_app = Application(
            gzip=self.gzip,
            debug=self.debug,
            static_path=self.static_path,
            handlers=self.handlers,
            cookie_secret=self.cookie_secret,
            login_url=self.login_url,
            xsrf_cookies=self.xsrf_cookies,
        )

        if self.debug and not self.autoreload:
            # FIXME hack to disable autoreload when debug is True
            from tornado import autoreload
            autoreload._reload_attempted = True
            autoreload._reload = lambda: None

        if self.ssl:
            ssl_options = dict(
                certfile=os.path.expanduser(self.ssl_certificate),
                keyfile=os.path.expanduser(self.ssl_certificate_key))
            self.server = HTTPServer(self._web_app, ssl_options=ssl_options)
        else:
            self.server = HTTPServer(self._web_app)

    def set_pid(self):
        if os.path.exists(self.pid_file):
            raise RuntimeError(
                "pid (%s) found in (%s)" % (self.pid,
                                            self.pid_file))
        else:
            with open(self.pid_file, 'w') as _file:
                _file.write(str(self.pid))
        signal.signal(signal.SIGTERM, self._inst_terminate_handler)
        signal.signal(signal.SIGINT, self._inst_kill_handler)
        self.logger.debug("PID stored (%s)" % self.pid)

    def remove_pid(self, quiet=False):
        error = None
        try:
            os.remove(self.pid_file)
        except OSError as error:
            if not quiet:
                self.logger.error(
                    'pid file not removed (%s); %s' % (self.pid_file, error))
        else:
            if not quiet:
                self.logger.debug("removed PID file: %s" % self.pid_file)

    def _init_basic_server(self):
        self.server.listen(port=self.port, address=self.host)
        IOLoop.instance().start()

    def spawn_instance(self):
        self.logger.debug("spawning tornado %s..." % self.uri)
        self.set_pid()
        self._init_basic_server()

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

    def _inst_stop(self, sig, delay=None):
        if self.child_pid:
            os.kill(self.child_pid, sig)
        else:
            self.stop(delay=delay)
        self.remove_pid(quiet=True)

    def _inst_terminate_handler(self, sig, frame):
        self.logger.debug("[INST] (%s) recieved TERM signal" % self.pid)
        self._inst_stop(sig)

    def _inst_kill_handler(self, sig, frame):
        self.logger.debug("[INST] (%s) recieved KILL signal" % self.pid)
        self._inst_stop(sig, 0)

    def _inst_delayed_stop(self, delay=None):
        if delay is None:
            if self.mconf.debug:
                delay = 0
            else:
                delay = 5
        self.logger.debug("stop ioloop called (%s)... " % self.pid)
        TIMEOUT = float(delay) + time.time()
        self.logger.debug("Shutting down in T-%i seconds ..." % delay)
        IOLoop.instance().add_timeout(TIMEOUT, self._stop_ioloop)

    def _stop_ioloop(self):
        IOLoop.instance().stop()
        self.logger.debug("IOLoop stopped")
