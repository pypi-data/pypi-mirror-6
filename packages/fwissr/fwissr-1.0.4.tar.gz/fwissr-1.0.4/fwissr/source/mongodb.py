"Mongodb Abstract Source code for fwissr"
from fwissr.source.abstract_source import AbstractSource
import copy
from ..conf import merge_conf
import urlparse
from pymongo import MongoClient

CONNECTIONS = {}


class Mongodb(AbstractSource):
    "A MongoDB base source that provides data for fwissr"
    @classmethod
    def from_settings(cls, settings):
        """Read Mongodb Source configuration from the provided settings"""
        if not 'mongodb' in settings or not 'collection' in settings or \
                settings['mongodb'] == '' or settings['collection'] == '':
            raise Exception(
                "Erroneous mongodb settings, "
                "needs a collection and mongodb setting",
                settings)

        cx_uri = urlparse.urlsplit(settings["mongodb"])
        db_name = cx_uri.path[1:]
        if db_name == "":
            raise Exception(
                "Erroneous mongodb settings, "
                "missing db_name", settings)

        cx_uri = urlparse.urlunsplit(
            (cx_uri.scheme, cx_uri.netloc, "/", cx_uri.query, cx_uri.fragment))
        options = copy.deepcopy(settings)
        del options['mongodb']
        del options['collection']

        return Mongodb(
            cls.connection_for_uri(cx_uri),
            db_name, settings['collection'], options)

    @classmethod
    def connection_for_uri(cls, uri):
        if not uri in CONNECTIONS:
            CONNECTIONS[uri] = MongoClient(uri)
        return CONNECTIONS[uri]

    TOP_LEVEL_COLLECTIONS = ['fwissr']

    def __init__(self, conn, db_name, collection_name, options):
        super(Mongodb, self).__init__(options)

        self._conn = conn
        self._db_name = db_name
        self._collection_name = collection_name

        self._collection = None

    def db_name():
        doc = "The db_name property."

        def fget(self):
            return self._db_name

        def fset(self, value):
            self._db_name = value

        def fdel(self):
            del self._db_name
        return locals()
    db_name = property(**db_name())

    def collection_name():
        doc = "The collection_name property."

        def fget(self):
            return self._collection_name

        def fset(self, value):
            self._collection_name = value

        def fdel(self):
            del self._collection_name
        return locals()
    collection_name = property(**collection_name())

    def fetch_conf(self):
        result = {}
        result_part = result

        if not self._collection_name in Mongodb.TOP_LEVEL_COLLECTIONS and (
                not 'top_level' in self._options
                or not self._options["top_level"]):
            for key_part in self._collection_name.split("."):
                if not key_part in result_part:
                    result_part[key_part] = {}
                result_part = result_part[key_part]

        conf = {}
        for doc in self.collection().find():
            key = doc['_id']
            if not 'value' in doc:
                del doc['_id']
                value = doc
            else:
                value = doc['value']
            conf[key] = value

        merge_conf(result_part, conf)
        return result

    def collection(self):
        if self._collection is None:
            self._collection = self._conn[self._db_name][self._collection_name]
        return self._collection
