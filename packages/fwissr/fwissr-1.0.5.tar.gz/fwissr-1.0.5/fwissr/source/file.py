# file.py
from abstract_source import AbstractSource
import copy
import glob
import os

from ..conf import parse_conf_file, merge_conf


class File(AbstractSource):
    TOP_LEVEL_CONF_FILES = ['fwissr']

    @classmethod
    def from_path(self, path, options={}):
        if path is None or path == '':
            raise Exception("Unexpected file path", path)
        return File(path, options)

    @classmethod
    def from_settings(self, settings={}):
        mine = copy.deepcopy(settings)
        del mine['filepath']
        return self.from_path(settings['filepath'], mine)

    def __init__(self, path, options={}):
        super(File, self).__init__(options)
        if not os.path.exists(path):
            raise Exception("Missing file", path)
        self._path = path

    def path():
        doc = "The path property."

        def fget(self):
            return self._path

        def fset(self, value):
            self._path = value

        def fdel(self):
            del self._path
        return locals()
    path = property(**path())

    def fetch_conf(self):
        result = {}

        if os.path.isdir(self._path):
            conf_files = []
            file_types = ("*.json", "*.yml", "*.yaml")
            for ftype in file_types:
                conf_files.extend(glob.glob(os.path.join(self._path, ftype)))
            conf_files.sort()
        else:
            conf_files = [self._path]

        for conf in conf_files:
            if os.path.isfile(conf):
                self.merge_conf_file(result, conf)

        return result

    def merge_conf_file(self, result, conf_file_path):
        "Merge a configuration in file with current configuration"
        conf = parse_conf_file(conf_file_path)
        conf_file_name = os.path.splitext(os.path.basename(conf_file_path))[0]
        result_part = result

        if not conf_file_name in File.TOP_LEVEL_CONF_FILES \
            and (
                not "top_level" in self._options
                or not self._options["top_level"]):
            for key_part in conf_file_name.split('.'):
                if not key_part in result_part:
                    result_part[key_part] = {}
                result_part = result_part[key_part]

        return merge_conf(result_part, conf)
