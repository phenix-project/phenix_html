import libtbx.load_env
import sys, os
from cStringIO import StringIO
import mmtbx.command_line.reciprocal_space_arrays

def run():
  log = StringIO()
  mmtbx.command_line.reciprocal_space_arrays.run(args=[], log = log)
  ofn = open("reciprocal_space_arrays.txt","w")
  ofn.write(log.getvalue())
  ofn.close()

if (__name__ == "__main__"):
  run()
