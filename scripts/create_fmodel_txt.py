import libtbx.load_env
import sys, os
from cStringIO import StringIO
import mmtbx.command_line.fmodel

def run():
  ofn = open("fmodel.txt","w")
  ofn.write(mmtbx.command_line.fmodel.legend)
  ofn.close()

if (__name__ == "__main__"):
  run()
