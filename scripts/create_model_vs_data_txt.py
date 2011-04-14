import libtbx.load_env
import sys, os
from cStringIO import StringIO
import mmtbx.model_vs_data

def run():
  log = StringIO()
  mmtbx.model_vs_data.run(args=[], log = log)
  ofn = open("model_vs_data.txt","w")
  ofn.write(log.getvalue())
  ofn.close()

if (__name__ == "__main__"):
  run()
