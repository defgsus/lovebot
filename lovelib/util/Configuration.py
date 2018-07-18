import json


class Configuration(object):

    def __init__(self, **kwargs):
        self._data = kwargs

    def __getattribute__(self, name):
        if name.startswith("_") or name in self.__class__.__dict__:
            return super().__getattribute__(name)
        return self._data[name]

    def __setattr__(self, key, value):
        if key.startswith("_") or key in self.__class__.__dict__:
            super().__setattr__(key, value)
        else:
            self._data[key] = value

    @classmethod
    def default_configuration(cls):
        return cls(
            world=cls(
                max_speed=5.,
                max_bots=128,
                max_bots_per_user=5,
            ),
            server=cls(
                host="127.0.0.1",
                port=8002,
                max_connections=100,
                user_pwd=[
                    ["admin", "admin"],
                    ["admin2", "admin"],
                ]
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
            return cls.from_json(fp.read())

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
            conf._data[key] = val
        return conf

    def to_json(self):
        data = dict()
        for key in self._data:
            val = self._data[key]
            if isinstance(val, Configuration):
                val = val.to_json()
            data[key] = val
        return data

    def save(self, filename=None):
        filename = filename or self.default_filename()
        with open(filename, "wt") as fp:
            json.dump(self.to_json(), fp, indent="    ")


if __name__ == "__main__":

    conf = Configuration.default_configuration()
    print(conf.default_filename())
    #conf.save()