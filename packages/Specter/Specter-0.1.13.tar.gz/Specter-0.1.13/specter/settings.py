import json
import six


class DictObj(object):
    def __init__(self, dictionary):
        self._base_dict = dictionary or {}

    def __getattr__(self, m):
        return self._base_dict.get(m, None)

    def __setattr__(self, m, v):
        super.__setattr__(self, m, v)

    @classmethod
    def dict_to_dotted(cls, dictionary):
        converted = {}
        for key, val in six.iteritems(dictionary):
            if isinstance(val, dict):
                converted[key] = DictObj.dict_to_dotted(val)
            else:
                converted[key] = val


class Settings(object):

    def __init__(self, filename=None):
        self._filename = filename
        self._loaded = False

    def __load__(self):
        fd = open(self._filename, 'r')
        self._body = json.load(fd)
        fd.close()

        self._loaded = True
