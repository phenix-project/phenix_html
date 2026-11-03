from __future__ import print_function
import libtbx.load_env
import os.path as op
import os
import re
import shutil
import subprocess
import tempfile

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

# the graph on the sitrep page is the picard run on the toxd regression data,
# with the logs its nodes link to
def example(docs_dir):
  data = libtbx.env.find_in_repositories(relative_path="phasertng_regression/DATA/toxd")
  if (data is None):
    print("No phasertng_regression/DATA/toxd, no example graph for sitrep.")
    return
  dest = op.join(docs_dir, "reference", "voyager_sitrep_example")
  work = tempfile.mkdtemp()
  database = op.join(work, "database")
  command = ["phasertng.picard"] + [op.join(data, f) for f in ["toxd.mtz", "toxd.pdb", "toxd.seq"]] + \
            ["database=" + database]
  with open(op.join(work, "picard.log"), "w") as log:
    returncode = subprocess.call(command, cwd=work, stdout=log, stderr=subprocess.STDOUT)
  if (returncode != 0):
    print("The picard run for the sitrep example failed, see %s" % op.join(work, "picard.log"))
    return
  if op.isdir(dest):
    shutil.rmtree(dest)
  os.makedirs(dest)
  links = set()
  for graph in ["graph_report.svg", "graph_report.html"]:
    shutil.copyfile(op.join(database, graph), op.join(dest, graph))
    with open(op.join(database, graph)) as f:
      links.update(re.findall(r'href=\\?"([^"\\]+)\\?"', f.read()))
  for link in sorted(links):
    source = op.join(database, link)
    if (not op.isfile(source)):
      continue
    if (not op.isdir(op.dirname(op.join(dest, link)))):
      os.makedirs(op.dirname(op.join(dest, link)))
    shutil.copyfile(source, op.join(dest, link))
  shutil.rmtree(work)

if (__name__ == "__main__"):
  run()
