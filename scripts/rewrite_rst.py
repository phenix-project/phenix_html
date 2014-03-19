
# XXX utility script for batch alteration of RST files on a per-line basis;
# originally written for adding headers above phil directives but can be
# repurposed as needed

import libtbx.load_env
import os.path

def run () :
  rst_dir = libtbx.env.find_in_repositories(
    relative_path="phenix_html/rst_files")
  for dirname, dirnames, filenames in os.walk(rst_dir) :
    for file_name in filenames :
      if (file_name != "doc_procedures.txt") :
        full_path = os.path.join(dirname, file_name)
        rst_in = open(full_path).read().splitlines()
        out = open(full_path, "w")
        for line in rst_in :
          if ("{{phil" in line) :
#            print >> out, ""
#            print >> out, "List of all available keywords"
#            print >> out, "------------------------------"
#            print >> out, ""
            print >> out, line
          else :
            print >> out, line
        out.close()

if (__name__ == "__main__") :
  run()
