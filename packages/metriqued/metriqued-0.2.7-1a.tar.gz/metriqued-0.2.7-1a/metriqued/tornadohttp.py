#!/usr/bin/env python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# Author: "Chris Ward <cward@redhat.com>

'''
metriqued.tornadohttp
~~~~~~~~~~~~~~~~~~~~~

This module contains the metriqued tornado web app
and server class, including configuration loading
and url handler definitions, start-up checks, etc.
'''

import logging
import os
from tornado.web import StaticFileHandler
import simplejson as json

from metriquet.tornadohttp import TornadoHTTPServer

from metriqued.config import metriqued_config, mongodb_config
from metriqued import core_api, cube_api, query_api, user_api

logger = logging.getLogger(__name__)

USER_DIR = os.path.expanduser('~/.metrique')
ETC_DIR = os.path.join(USER_DIR, 'etc')
METRIQUED_JSON = os.path.join(ETC_DIR, 'metriqued.json')


def user_cube(value):
    user_cube = r'(\w+)/([-\w]+)'
    path = os.path.join(user_cube, str(value))
    return path


def api_v2(value):
    return os.path.join(r'/api/v2', str(value))


def api_v1(value):
    return os.path.join(r'/api/v1', str(value))


def ucv2(value):
    uc = user_cube(value)
    a2 = api_v2(uc)
    return a2


class MongoDBHandler(logging.StreamHandler):
    def __init__(self, collection):
        super(MongoDBHandler, self).__init__()
        self.collection = collection

    def emit(self, record):
        r = record
        try:
            msg = json.loads(r.getMessage())
        except Exception:
            msg = r.getMessage()
        obj = {
            'args': r.args,
            'created': r.created,
            'funcname': r.funcName,
            'levelname': r.levelname,
            'levelno': r.levelno,
            'module': r.module,
            'msecs': r.msecs,
            'message': msg,
            'name': r.name,
            'process': r.process,
            'thread': r.thread,
        }
        self.collection.insert(obj)


class MetriqueHTTP(TornadoHTTPServer):
    ''' HTTP (Tornado >=3.0) implemntation of MetriqueServer '''
    name = 'metriqued'

    def __init__(self, config_file=None, **kwargs):
        config_file = config_file or METRIQUED_JSON

        self.config = metriqued_config(config_file=config_file, **kwargs)
        self.dbconf = mongodb_config(self.config.mongodb_config)

        # call setup_logger() after loading config
        # results in a .logger and .request_logger attrs
        self.setup_logger()

        logger.debug('======= metrique =======')
        logger.debug(' pid:  %s' % self.pid)
        logger.debug(' Conf: %s' % self.config.config_file)
        logger.debug(' Host: %s' % self.uri)
        logger.debug('  SSL: %s' % self.config.ssl)
        logger.debug('======= mongodb ========')
        logger.debug(' Conf: %s' % self.dbconf.config_file)
        logger.debug(' Host: %s' % self.dbconf.host)
        logger.debug('  SSL: %s' % self.dbconf.ssl)
        logger.debug(' Port: %s' % self.dbconf.port)

        self._mongodb_check()
        self._prepare_handlers()
        self._setup_mongodb_request_logging()

    def _prepare_handlers(self):
        # pass in metrique and mongodb config to all handlers (init)
        init = dict(metrique_config=self.config,
                    mongodb_config=self.dbconf)

        api_docs = self.config.api_docs
        base_handlers = [
            (r"/api/v2/docs/(.*)", StaticFileHandler, {'path': api_docs}),

            (r"/register", user_api.RegisterHdlr, init),
            (r"/login", user_api.LoginHdlr, init),
            (r"/logout", user_api.LogoutHdlr, init),

            (r"/(\w+)/aboutme", user_api.AboutMeHdlr, init),
            (r"/(\w+)/passwd", user_api.UpdatePasswordHdlr, init),
            (r"/(\w+)/remove", user_api.RemoveHdlr, init),
            (r"/(\w+)/update_profile", user_api.UpdateProfileHdlr, init),
            (r"/(\w+)/update_properties", user_api.UpdatePropertiesHdlr, init),

            (api_v1(r""), core_api.ObsoleteAPIHdlr, init),
            (api_v2(r"ping"), core_api.PingHdlr, init),

            (api_v2(r"(\w+)?/?([-\w]+)?"), cube_api.ListHdlr, init),
        ]

        user_cube_handlers = [
            (ucv2(r"find"), query_api.FindHdlr, init),
            (ucv2(r"history"), query_api.HistoryHdlr, init),
            (ucv2(r"deptree"), query_api.DeptreeHdlr, init),
            (ucv2(r"count"), query_api.CountHdlr, init),
            (ucv2(r"aggregate"), query_api.AggregateHdlr, init),
            (ucv2(r"distinct"), query_api.DistinctHdlr, init),
            (ucv2(r"sample"), query_api.SampleHdlr, init),

            (ucv2(r"index"), cube_api.IndexHdlr, init),
            (ucv2(r"save"), cube_api.SaveObjectsHdlr, init),
            (ucv2(r"rename"), cube_api.RenameHdlr, init),
            (ucv2(r"remove"), cube_api.RemoveObjectsHdlr, init),
            (ucv2(r"export"), cube_api.ExportHdlr, init),
            (ucv2(r"update_role"), cube_api.UpdateRoleHdlr, init),
            (ucv2(r"drop"), cube_api.DropHdlr, init),
            (ucv2(r"stats"), cube_api.StatsHdlr, init),
            (ucv2(r"register"), cube_api.RegisterHdlr, init),
        ]

        handlers = base_handlers + user_cube_handlers
        self.handlers = handlers
        return handlers

    def _mongodb_check(self):
        # Fail to start if we can't communicate with mongo
        host = self.dbconf.host
        logger.debug('testing mongodb connection status (%s) ...' % host)
        try:
            assert self.dbconf.db_metrique_admin.db
            assert self.dbconf.db_timeline_admin.db
            assert self.dbconf.db_metrique_data.db
            assert self.dbconf.db_timeline_data.db
            logger.debug('... mongodb connection ok')
        except Exception:
            logger.error(
                'failed to communicate with mongodb')
            raise

    def _setup_mongodb_request_logging(self):
        if self.config.log2mongodb:
            logger = logging.getLogger(self.config.log_requests_name)
            # FIXME: make handler-reset optional?
            logger.handlers = []  # remove existing (file) handler
            hdlr = MongoDBHandler(collection=self.dbconf.c_logs_admin)
            logger.addHandler(hdlr)
