import json


class Configuration(object):

    class Values(object):
        def __init__(self, **data):
            self._data = data

        def __getattribute__(self, key):
            if key.startswith("_"):
                return object.__getattribute__(self, key)
            return self._data[key]

        def __setattr__(self, key, value):
            if key.startswith("_"):
                super().__setattr__(key, value)
            else:
                self._data[key] = value

    def __init__(self, **kwargs):
        self.v = self.Values(**kwargs)

    @classmethod
    def default_configuration(cls):
        return cls(
            world=cls.Values(
                max_speed=5.,
                max_bots=128,
                max_bots_per_user=5,
            ),
            server=cls.Values(
                port=8001,
                max_connections=100,
            ),
        )

    @classmethod
    def default_filename(cls):
        import os
        return os.path.join(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
            "loveconfig.json"
        )

    @classmethod
    def from_file(cls, filename=None):
        filename = filename or cls.default_filename()
        with open(filename, "rt") as fp:
            return cls.from_json(fp)

    @classmethod
    def from_json(cls, object_or_str):
        if isinstance(object_or_str, str):
            data = json.loads(object_or_str)
        else:
            data = object_or_str

        conf = cls()
        for key in data:
            val = data[key]
            if isinstance(val, dict):
                val = cls.from_json(val)
            conf.v._data[key] = val
        return conf

    def _to_json(self, instance):
        if isinstance(instance, self.Values):
            _data = instance._data
        else:
            _data = instance.v._data
        data = dict()
        for key in _data:
            val = _data[key]
            if isinstance(val, (Configuration, self.Values)):
                val = self._to_json(val)
            data[key] = val
        return data

    def save(self, filename=None):
        filename = filename or self.default_filename()
        with open(filename, "wt") as fp:
            json.dump(self._to_json(self), fp, indent="    ")


if __name__ == "__main__":

    conf = Configuration.default_configuration()
    print(conf.default_filename())
    #conf.save()