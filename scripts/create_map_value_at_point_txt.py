import libtbx.load_env
import sys, os
from cStringIO import StringIO
import mmtbx.command_line.map_value_at_point

def run():
  log = StringIO()
  mmtbx.command_line.map_value_at_point.run(args=[], log = log)
  ofn = open("map_value_at_point.txt","w")
  ofn.write(log.getvalue())
  ofn.close()

if (__name__ == "__main__"):
  run()
