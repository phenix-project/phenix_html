import mmtbx.model_vs_data
import libtbx.load_env
from cStringIO import StringIO
import os.path as op
import os
import sys

def run():
  html_dir = libtbx.env.find_in_repositories(relative_path="phenix_html")
  dest_dir = op.join(html_dir, "rst_files", "reference")
  log = StringIO()
  print >> log, mmtbx.model_vs_data.msg
  print >> log, """Default parameters:\n{{phil:mmtbx.model_vs_data}}"""
  ofn = open(op.join(dest_dir, "model_vs_data.txt"), "w")
  ofn.write(log.getvalue())
  ofn.close()

if (__name__ == "__main__"):
  run()
