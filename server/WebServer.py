import os
from io import BytesIO

import tornado.web

from lovelib.server import LoveServer


class WebServer(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resources = {
            "/index.html", "/main.css", "/main.js", "/jquery.js",
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
                    self.loaded_resources[r] = f.read()
            else:
                if r == "/worldmap.png":
                    data = BytesIO()
                    LoveServer.instance().world.df.save_png(data, 320, 320)
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
        if url.endswith(".css"):
            self.set_header("Content-Type", "text/css")
        elif url.endswith(".js"):
            self.set_header("Content-Type", "text/javascript")
        #self.write("<pre>args=%s\nkwargs=%s\nreq=%s</pre>" % (args, kwargs, self.request))

