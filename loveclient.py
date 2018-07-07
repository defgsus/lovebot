import time
from lovelib.client import LoveClient


client = LoveClient("ws://127.0.0.1:8001/ws")

for i in range(5):
    time.sleep(1)
    client.write_message("hallo%s" % i)


