import os
from io import BytesIO

import tornado.web

from lovelib.server import LoveServer
from lovelib.util import Configuration


class WebServer(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        if "config" in kwargs:
            self.config = kwargs.pop("config")
        else:
            self.config = Configuration.default_configuration()
        super().__init__(*args, **kwargs)
        self.resources = {
            "/index.html", "/main.css", "/main.js", "/jquery.js", "/favicon.ico",
        }
        self.templates = {
            "/main.js": lambda s: s.decode("utf-8").replace("{{host}}", self.config.server.host).replace("{{port}}", str(self.config.server.port)).encode("utf-8")
        }
        self.loaded_resources = dict()
        self.resource_path = os.path.join(os.path.dirname(__file__), "web")

    def get_resource_filename(self, r):
        return os.path.join(self.resource_path, r.strip("/"))

    def get_resource(self, r):
        if r not in self.loaded_resources:
            if r in self.resources:
                fn = self.get_resource_filename(r)
                with open(fn, "rb") as f:
                    data = f.read()
                    if r in self.templates:
                        data = self.templates[r](data)
                    self.loaded_resources[r] = data
            else:
                if r == "/worldmap.png":
                    data = BytesIO()
                    LoveServer.instance().world.df.save_png(
                        data, 640, 640,
                        bounding_box=LoveServer.instance().world.df.bounding_box(),
                    )
                    data.seek(0)
                    self.loaded_resources[r] = data.read()
                else:
                    raise KeyError("resource %s not known" % r)
        return self.loaded_resources[r]

    def get(self, *args, **kwargs):
        url = self.request.uri
        print("GET", self.request)
        if url == "/":
            url = "/index.html"
        self.write(self.get_resource(url))
        for ext, ctype in (
                ("css", "text/css"),
                ("js", "text/javascript"),
                ("png", "image/png"),
        ):
            if url.endswith(".%s" % ext):
                self.set_header("Content-Type", ctype)
                break
        #self.write("<pre>args=%s\nkwargs=%s\nreq=%s</pre>" % (args, kwargs, self.request))

