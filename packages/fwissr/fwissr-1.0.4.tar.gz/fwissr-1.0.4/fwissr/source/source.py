from file import File
from mongodb import Mongodb


class Source(object):
    @classmethod
    def from_settings(self, settings):
        if not isinstance(settings, dict):
            raise Exception("Unexpected source settings class", settings)

        if 'filepath' in settings:
            return File.from_settings(settings)
        elif 'mongodb' in settings:
            return Mongodb.from_settings(settings)
        else:
            raise Exception("Unexpected source settings kind", settings)
