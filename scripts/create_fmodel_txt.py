import libtbx.load_env
import sys, os
from cStringIO import StringIO
import mmtbx.command_line.fmodel

def run():
  log = StringIO()
  mmtbx.command_line.fmodel.run(args=[], log = log)
  ofn = open("fmodel.txt","w")
  ofn.write(log.getvalue())
  ofn.close()

if (__name__ == "__main__"):
  run()
