import libtbx.load_env
from cStringIO import StringIO
import mmtbx.command_line.maps
import os.path as op
import os

def run():
  html_dir = libtbx.env.find_in_repositories(relative_path="phenix_html")
  dest_dir = op.join(html_dir, "rst_files", "reference")
  os.chdir(dest_dir)
  log = StringIO()
  mmtbx.command_line.maps.run(args=["NO_PARAMETER_FILE"], log = log)
  ofn = open("phenix_maps.txt","w")
  ofn.write(log.getvalue())
  ofn.close()

if (__name__ == "__main__"):
  run()
