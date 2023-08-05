from threading import RLock, Thread

from conf import merge_conf
import UserDict
import UserList
import time


class ReadOnlyList(UserList.UserList):
    def __setitem__(self, i, item):
        raise TypeError

    def update(self, array=None):
        if array is None:
            pass
        elif isinstance(array, UserList.UserList):
            self.data = array.data
        elif isinstance(array, type([])):
            self.data = array
        else:
            raise TypeError


class ReadOnlyDict(UserDict.IterableUserDict):
    def __setitem__(self, key, item):
        raise TypeError

    def __delitem__(self, key):
        raise TypeError

    def clear(self):
        raise TypeError

    def pop(self, key, *args):
        raise TypeError

    def popitem(self):
        raise TypeError

    def update(self, dict=None):
        if dict is None:
            pass
        elif isinstance(dict, UserDict.UserDict):
            self.data = dict.data
        elif isinstance(dict, type({})):
            self.data = dict
        else:
            raise TypeError


class ReloadThread(Thread):
    def __init__(self, registry):
        super(ReloadThread, self).__init__()
        self._registry = registry

    def run(self):
        count = 0
        while True:
            time.sleep(1)
            if count == self._registry.refresh_period:
                self._registry.load()
                count = 0
            count += 1


class Registry:
    DEFAULT_REFRESH_PERIOD = 30

    def __init__(self, refresh_period=DEFAULT_REFRESH_PERIOD):
        self._refresh_period = refresh_period

        self._registry = {}
        self._frozen = False
        self.sources = []

        self.semaphore = RLock()
        self.refresh_thread = None

    def frozen():
        doc = "The frozen property."

        def fget(self):
            return self._frozen

        def fset(self, value):
            self._frozen = value

        def fdel(self):
            del self._frozen

        return locals()
    frozen = property(**frozen())

    def refresh_period():
        doc = "The refresh_period property."

        def fget(self):
            return self._refresh_period
        return locals()
    refresh_period = property(**refresh_period())

    def add_source(self, source):
        with self.semaphore:
            self.sources.append(source)

        if self._frozen:
            self.reload()
        else:
            with self.semaphore:
                merge_conf(self._registry, source.get_conf())

        self.ensure_refresh_thread()
        self.ensure_frozen()

    def reload(self):
        self.reset()
        self.load()

    def deep_freeze(self, what):
        if isinstance(what, dict) or isinstance(what, UserDict.UserDict):
            w = {}
            for (key, value) in what.items():
                if(isinstance(value, dict)
                        or isinstance(value, UserDict.UserDict)):
                    w[key] = self.deep_freeze(value)
                elif (isinstance(value, type([]))
                        or isinstance(value, UserList.UserList)):
                    w[key] = self.deep_freeze(value)
                else:
                    w[key] = value
            r = ReadOnlyDict()
            r.update(w)
            return r
        elif isinstance(what, type([])) or isinstance(what, UserList.UserList):
            r = ReadOnlyList()
            r.update(what)
            return r
        else:
            raise Exception("Deep Freezine failed for", what)

    def get(self, key):
        key_ary = key.split("/")

        if key_ary[0] == "":
            key_ary.pop(0)

        if key_ary[-1] == "":
            key_ary.pop(len(key_ary)-1)

        cur_hash = self._registry
        for key_component in key_ary:
            if key_component in cur_hash:
                cur_hash = cur_hash[key_component]
            else:
                return None

        return cur_hash

    def __getitem__(self, key):
        return self.get(key)

    def keys(self):
        result = []
        self._keys(result, [], self._registry)
        return sorted(result)

    def dump(self):
        return self._registry

    def have_refreshable_source(self):
        with self.semaphore:
            return True in [source.can_refresh() for source in self.sources]
            return False

    def ensure_refresh_thread(self):
        if(self.refresh_period > 0) and self.have_refreshable_source() \
            and (
                self.refresh_thread is None or
                not self.refresh_thread.is_alive()):
            # re-start refresh thread
            self.refresh_thread = ReloadThread(self)
            self.refresh_thread.daemon = True
            self.refresh_thread.start()

    def ensure_frozen(self):
        if not self._frozen:
            with self.semaphore:
                self._registry = self.deep_freeze(self._registry)
                self._frozen = True

    def reset(self):
        with self.semaphore:
            self._registry = {}
            self._frozen = False
            [source.reset() for source in self.sources]

    def load(self):
        with self.semaphore:
            self._registry = {}
            self.frozen = False
            for source in self.sources:
                source_conf = source.get_conf()
                merge_conf(self._registry, source_conf)
        # print "Reloaded with content: %s" % self

    def registry():
        doc = "The registry property."

        def fget(self):
            self.ensure_refresh_thread
            return self._registry
        return locals()
    registry = property(**registry())

    def _keys(self, result, key_ary, dct):
        for (key, value) in dct.items():
            key_ary.append(key)
            result.append("/%s" % ("/".join(key_ary)))
            if isinstance(value, dict) or isinstance(value, UserDict.UserDict):
                self._keys(result, key_ary, value)
            key_ary.pop()
