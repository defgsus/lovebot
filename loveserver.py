import os
import sys
import argparse

import server.mainloop
from lovelib.util import Configuration


CONFIG_FILENAME = Configuration.default_filename()

config = Configuration.default_configuration()


parser = argparse.ArgumentParser()
parser.add_argument("-c", nargs=1, type=str,
                    help="Set config filename")
parser.add_argument("-d", nargs="?", const=True,
                    help="Output default config file")

options = parser.parse_args(sys.argv[1:])

if options.c:
    CONFIG_FILENAME = options.c[0]

if options.d:
    config.save(CONFIG_FILENAME)
    print("written default config to %s" % CONFIG_FILENAME)
    exit()

if os.path.exists(CONFIG_FILENAME):
    print("using config file %s" % CONFIG_FILENAME)
    config = Configuration.from_file(CONFIG_FILENAME)
    #print(config._to_json(config))

server.mainloop.run(config=config)



