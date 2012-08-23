
from phenix.utilities import toc_and_index
from libtbx.utils import Sorry, null_out
from libtbx import easy_run
import libtbx.load_env
import shutil
import os
import re
import sys

def run (out=None, log=None) :
  if (out is None) : out = sys.stdout
  if (log is None) : log = null_out()
  html_dir = libtbx.env.find_in_repositories(
    relative_path="phenix_html",
    test=os.path.isdir)
  if (html_dir is None) :
    raise Sorry("phenix_html repository not found.")
  sys.path.append(os.path.join(html_dir, "scripts")) # XXX gross!
  import raw_from_rst_html
  import create_refinement_txt
  import create_fmodel_txt
  import create_phenix_maps
  import create_map_value_at_point_txt
  import create_reciprocal_space_arrays_txt
  import create_model_vs_data_txt
  top_dir = os.path.dirname(html_dir)
  docs_dir = os.path.join(top_dir, "doc")
  os.chdir(html_dir)
  print >> out, "Building PHENIX documentation in %s" % html_dir
  print >> out, "The complete documentation will be in:"
  print >> out, "  %s" % docs_dir
  print >> out, "  creating restructured text files"
  rst_dir = os.path.join(html_dir, "rst_files")
  os.chdir(rst_dir)
  create_refinement_txt.run()
  create_fmodel_txt.run()
  create_phenix_maps.run()
  create_map_value_at_point_txt.run()
  create_reciprocal_space_arrays_txt.run()
  create_model_vs_data_txt.run()
  print >> out, "  building HTML files from restructured text files"
  rst_files = os.listdir(rst_dir)
  html_files = []
  for file_name in rst_files :
    if (not file_name.endswith(".txt")) : continue
    disable = ("disable_rst2html" in open(file_name).read())
    if (not disable) :
      html_name = os.path.splitext(file_name)[0] + ".html"
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
    f = open(os.path.join(html_dir, "raw_files", raw_file), "w")
    raw_from_rst_html.run(args=[file_name], out=f)
    f.close()
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
  run()
