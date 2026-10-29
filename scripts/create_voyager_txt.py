from __future__ import print_function
import libtbx.load_env
import os.path as op
import os
import shutil

# the voyager pages are written by the phasertng build (scons_scripts/write_voyager_doc.py)
# from phasertng/doc/pre; edit them there, not here
html_dir = libtbx.env.find_in_repositories(relative_path="phenix_html")
dest_dir = op.join(html_dir, "rst_files", "reference")
marker = ".. written by the phasertng build"

def run():
  doc_dir = libtbx.env.find_in_repositories(relative_path="phasertng/doc")
  if (doc_dir is None):
    print("No phasertng/doc directory found.")
    return
  for file_name in sorted(os.listdir(doc_dir)):
    if (not file_name.endswith(".txt")):
      continue
    name = op.splitext(file_name)[0]
    dest = op.join(dest_dir, file_name)
    # a page written by hand is replaced only once the voyager page has its prose
    pre = op.join(doc_dir, "pre", name + ".pre")
    if (op.isfile(dest) and not op.isfile(pre)):
      with open(dest) as f:
        if (not f.readline().startswith(marker)):
          continue
    shutil.copyfile(op.join(doc_dir, file_name), dest)

if (__name__ == "__main__"):
  run()
