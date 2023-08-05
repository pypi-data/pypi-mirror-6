class AbstractSource(object):

    def __init__(self, options={}):
        self.reset()
        self._options = options

    def reset(self):
        self._conf = None

    def can_refresh(self):
        if 'refresh' in self._options and self._options['refresh']:
            return True
        return False

    def get_conf(self):
        if self._conf is None or self.can_refresh():
            self._conf = self.fetch_conf()
        return self._conf

    def fetch_conf(self):
        raise Exception("Not implemented")
