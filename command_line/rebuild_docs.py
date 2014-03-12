
from __future__ import division
from phenix.utilities import toc_and_index
from libtbx.utils import Sorry, null_out, import_python_object
import libtbx.phil.command_line
from libtbx import easy_run
import libtbx.load_env
import os.path as op
import shutil
import time
import os
import re
import sys

master_phil_str = """
force = False
  .type = bool
"""

# FIXME this is an improvement over separate scripts to create these files,
# but it makes it impossible to combine the command-line and GUI documentation
create_rst_from_modules = [
  ("mmtbx.command_line.reciprocal_space_arrays","reciprocal_space_arrays.txt"),
  ("mmtbx.command_line.map_value_at_point", "map_value_at_point.txt"),
  ("mmtbx.command_line.fmodel", "fmodel.txt"),
]

def run (args=(), out=None, log=None) :
  cmdline = libtbx.phil.command_line.process(
    args=args,
    master_string=master_phil_str)
  params = cmdline.work.extract()
  if (out is None) : out = sys.stdout
  if (log is None) : log = null_out()
  html_dir = libtbx.env.find_in_repositories(
    relative_path="phenix_html",
    test=os.path.isdir)
  if (html_dir is None) :
    raise Sorry("phenix_html repository not found.")
  rst_dir = op.join(html_dir, "rst_files")
  raw_dir = op.join(html_dir, "raw_files")
  sys.path.append(os.path.join(html_dir, "scripts")) # XXX gross!
  import raw_from_rst_html
  # FIXME these need to go away
  import create_refinement_txt
  import create_phenix_maps
  import create_model_vs_data_txt
  top_dir = os.path.dirname(html_dir)
  docs_dir = os.path.join(top_dir, "doc")
  os.chdir(html_dir)
  print >> out, "Building PHENIX documentation in %s" % html_dir
  print >> out, "The complete documentation will be in:"
  print >> out, "  %s" % docs_dir
  print >> out, "  creating restructured text files"
  os.chdir(rst_dir)
  create_refinement_txt.run()
  create_phenix_maps.run()
  create_model_vs_data_txt.run()
  for module_name, rst_file in create_rst_from_modules :
    print >> out, "    %s" % rst_file
    legend = import_python_object(
      import_path=module_name+".legend",
      error_prefix="",
      target_must_be="",
      where_str="").object
    open(op.join(rst_dir, rst_file), "w").write(legend)
  print >> out, "  building HTML files from restructured text files"
  if (not params.force) :
    print >> out, \
      "      processing modified files only (override with --force)"
  rst_files = os.listdir(rst_dir)
  html_files = []
  def _cmp_make(f1, f2):
    if os.stat(f1).st_mtime < os.stat(f2).st_mtime: return 1
    return -1
  rst_files.sort(_cmp_make)
  for file_name in rst_files:
    if (not file_name.endswith(".txt")) : continue
    disable = ("disable_rst2html" in open(file_name).read())
    if (not disable) :
      html_name = os.path.splitext(file_name)[0] + ".html"
      raw_file = op.join(raw_dir, op.splitext(file_name)[0] + ".raw")
      if op.exists(raw_file) and not params.force :
        if (op.getmtime(raw_file) > op.getmtime(file_name)) :
          continue
      print >> out, "    converting %s to %s" % (os.path.basename(file_name),
        os.path.basename(html_name))
      stdout_lines = easy_run.fully_buffered(
        ["docutils.rst2html", file_name]).raise_if_errors().stdout_lines
      f = open(html_name, "w")
      for line in stdout_lines :
        print >> f, line
      f.close()
      html_files.append(os.path.join(rst_dir, html_name))
  print >> out, "  converting restructured text HTML files to raw HTML files"
  for file_name in html_files :
    raw_file = os.path.splitext(os.path.basename(file_name))[0] + ".raw"
    #print >> out, "    converting %s to %s" % (os.path.basename(file_name),
    #  raw_file)
    f = open(os.path.join(raw_dir, raw_file), "w")
    raw_from_rst_html.run(args=[file_name], out=f)
    f.close()
    os.remove(file_name)
  print >> out, \
    "  converting raw HTML files, creating tables-of-contents, and indexing"
  os.chdir(html_dir)
  toc_and_index.run(args=(), out=log)
  assert os.path.isfile("phenix_index.htm")
  print >> out, "  populating documentation directory %s" % docs_dir
  if (os.path.exists(docs_dir)) :
    shutil.rmtree(docs_dir)
  os.makedirs(docs_dir)
  shutil.copytree(os.path.join(html_dir, "icons"),
                  os.path.join(docs_dir, "icons"))
  shutil.copytree(os.path.join(html_dir, "images"),
                  os.path.join(docs_dir, "images"))
  for file_name in os.listdir(html_dir) :
    if (file_name.endswith(".html")) :
      shutil.copy(file_name, docs_dir)
    elif (file_name.endswith(".htm")) :
      shutil.move(file_name, docs_dir)
  os.chdir(docs_dir)
  phenix_version = os.environ.get("PHENIX_VERSION", None)
  release_tag = os.environ.get("PHENIX_RELEASE_TAG", None)
  if (None in [phenix_version, release_tag]) :
    version = "unknown (built %s)" % time.strftime("%b %d %Y", time.localtime())
  else :
    version = "%s-%s" % (phenix_version, release_tag)
  index_in = open("phenix_documentation.html").readlines()
  index_out = open("phenix_documentation.html", "w")
  for line in index_in :
    if ("INSTALLED_VERSION" in line) :
      print >> index_out, re.sub("INSTALLED_VERSION", version, line)
    else :
      print >> index_out, line
  if (sys.platform == "win32") :
    shutil.copy("phenix_documentation.html", "index.html")
  else :
    os.symlink("phenix_documentation.html", "index.html")

if (__name__ == "__main__") :
  run(args=sys.argv[1:])
