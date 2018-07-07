import os

import tornado.web


class WebServer(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resources = {
            "/index.html", "/main.css", "/main.js"
        }
        self.loaded_resources = dict()
        self.resource_path = os.path.join(os.path.dirname(__file__), "web")

    def get_resource_filename(self, r):
        return os.path.join(self.resource_path, r.strip("/"))

    def get_resource(self, r):
        if r not in self.resources:
            raise KeyError("resource %s not known" % r)
        if r not in self.loaded_resources:
            fn = self.get_resource_filename(r)
            with open(fn, "rb") as f:
                self.loaded_resources[r] = f.read()
        return self.loaded_resources[r]

    def get(self, *args, **kwargs):
        url = self.request.uri
        print("GET", self.request)
        if url == "/":
            url = "/index.html"
        if url in self.resources:
            self.write(self.get_resource(url))
        else:
            self.write("<pre>args=%s\nkwargs=%s\nreq=%s</pre>" % (args, kwargs, self.request))

