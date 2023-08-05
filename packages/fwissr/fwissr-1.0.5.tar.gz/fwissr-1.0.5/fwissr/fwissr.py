#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from registry import Registry
from source.source import Source
from conf import parse_conf_file, merge_conf


class FwissrModule(object):
    # main conf file
    MAIN_CONF_FILE = "fwissr.json"
    # default path where main conf file is located
    DEFAULT_MAIN_CONF_PATH = "/etc/fwissr"
    # default directory (relative to current user's home)
    # where user's main conf file is located
    DEFAULT_MAIN_USER_CONF_DIR = ".fwissr"

    def __init__(self):
        self._main_conf_path = self.DEFAULT_MAIN_CONF_PATH
        self._main_user_conf_path = os.path.join(
            self.find_home(),
            self.DEFAULT_MAIN_USER_CONF_DIR)
        self._global_registry = None
        self._main_conf = None
        self._main_conf_file = None
        self._main_user_conf_file = None

    def main_conf_path():
        doc = "The main_conf_path property."

        def fget(self):
            return self._main_conf_path

        def fset(self, value):
            self._main_conf_path = value
        return locals()
    main_conf_path = property(**main_conf_path())

    def main_user_conf_path():
        doc = "The main_user_conf_path property."

        def fget(self):
            return self._main_user_conf_path

        def fset(self, value):
            self._main_user_conf_path = value
        return locals()
    main_user_conf_path = property(**main_user_conf_path())

    def find_home(self):
        for v in ('HOME', 'USERPROFILE'):
            if v in os.environ:
                return os.environ[v]

        if "HOMEDRIVE" in os.environ and "HOMEPATH" in os.environ:
            return "%s:%s" % (os.environ["HOMEDRIVE"], os.environ["HOMEPATH"])

        try:
            return os.path.expanduser("~")
        except Exception:
            if os.sep == '\\':
                return "C:/"
            else:
                return "/"

    def parse_args(self, argv):
        pass

    def global_registry(self):
        """Global Registry


        NOTE: Parses main conf files (/etc/fwissr/fwissr.json
            and ~/.fwissr/fwissr.json)

        then uses 'fwissr_sources' setting to setup additional sources

        Example of /etc/fwissr/fwissr.json file:

         {
           'fwissr_sources': [
             { 'filepath': '/mnt/my_app/conf/' },
             { 'filepath': '/etc/my_app.json' },
             { 'mongodb': 'mongodb://db1.example.net/my_app',
                 'collection': 'config', 'refresh': true },
           ],
           'fwissr_refresh_period': 30,
        }
        access global registry with Fwissr['/foo/bar']
        """
        if self._global_registry is None:
            if 'fwissr_refresh_period' in self.main_conf:
                result = Registry(
                    refresh_period=self.main_conf['fwissr_refresh_period'])
            else:
                result = Registry()

            if (os.path.exists(self.main_conf_path) or
                    os.path.exists(self.main_user_conf_path)):

                if os.path.exists(self.main_conf_path):
                    result.add_source(
                        Source.from_settings(
                            {'filepath': self.main_conf_path}))

                if os.path.exists(self.main_user_conf_path):
                    result.add_source(
                        Source.from_settings(
                            {'filepath': self.main_user_conf_path}))

                if 'fwissr_sources' in self.main_conf:
                    for source in self.main_conf['fwissr_sources']:
                        result.add_source(Source.from_settings(source))

            self._global_registry = result
        return self._global_registry

    def main_conf():
        doc = "The main_conf property."

        def fget(self):
            if self._main_conf is None:
                result = {}
                if os.path.exists(self.main_conf_file):
                    result = merge_conf(
                        result,
                        parse_conf_file(self.main_conf_file))

                if os.path.exists(self.main_user_conf_file):
                    result = merge_conf(
                        result,
                        parse_conf_file(self.main_user_conf_file))

                self._main_conf = result
            return self._main_conf
        return locals()
    main_conf = property(**main_conf())

    def main_conf_file():
        doc = "The main_conf_file property."

        def fget(self):
            if self._main_conf_file is None:
                self._main_conf_file = os.path.join(
                    self.main_conf_path,
                    self.MAIN_CONF_FILE)

            return self._main_conf_file
        return locals()
    main_conf_file = property(**main_conf_file())

    def main_user_conf_file():
        doc = "The main_user_conf_file property."

        def fget(self):
            if self._main_user_conf_file is None:
                self._main_user_conf_file = os.path.join(
                    self.main_user_conf_path,
                    self.MAIN_CONF_FILE)

            return self._main_user_conf_file
        return locals()
    main_user_conf_file = property(**main_user_conf_file())

    def get(self, key):
        return self.global_registry().get(key)

    def __getitem__(self, key):
        return self.global_registry().get(key)

    def keys(self):
        return self.global_registry().keys()

    def dump(self):
        return self.global_registry().dump()

Fwissr = FwissrModule()
