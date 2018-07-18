## Lovebot

This is a lovely robot simulation running on a webserver.

`loveserver.py` starts an http server that delivers a website to view the arena 
and a websocket server for observers and robot lovers.

A simple client controlling a few bots is in the `examples` folder.

Bots live in a 2D world, constrained by solid objects and are themselves just circles 
with [Braitenberg vehicle](https://en.wikipedia.org/wiki/Braitenberg_vehicle)-style
wheels. The wheel-speed can be set individually for both wheels.

The world can be [ray traced](https://en.wikipedia.org/wiki/Ray_tracing_(graphics)) to
find intersections with objects or bots. More precisely, the world is described by
simple geometric objects that allow the efficient calculation of the distance 
to the next object's surface at any given point, 
a technique called [sphere tracing](https://duckduckgo.com/?q=sphere+tracing).

Basically, a client looks like this:

```python
from lovelib.client import LoveClient

class MyLoveClient(LoveClient):

    def on_connect(self):
        self.bot = self.create_bot(name="Dieter") 

    def on_event(self, name, data):
        pass

    # called regularily
    def on_update(self, delta_time):
        # test distance to object at fixed location
        d = self.world.distance_to(1, 2) 
        # find surface closest to bot in a certain direction
        t = self.bot.trace_front()
        t = self.bot.trace_degree(45)
        # control movement
        self.bot.set_wheel_speed(3, 4)
        
MyLoveClient("host", "user", "password").mainloop()
```