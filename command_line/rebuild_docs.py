
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

def raw_from_rst_html (file_name, dirname=None, out=None):
  raw_header_1 = """\
<!--REMARK PHENIX TITLE START  Put your title here>


<H4><U>"""

  raw_header_2 = """</U></H4>


<!--REMARK PHENIX TITLE END-->

<!--REMARK PHENIX BODY START   Put your text here.
Anything enclosed in header html H4 H5 etc will go in the table of contents>
"""

  raw_footer = """\
<!--REMARK PHENIX BODY END-->
"""
  if (out is None) : out = sys.stdout
  title = ""
  lines_init = iter(open(file_name).read().splitlines())
  for line in lines_init:
    if (line.startswith('<h1 class="title">')):
      line = line[18:]
      line = line[:line.rfind("<")]
      title = line

  lines = iter(open(file_name).read().splitlines())
  for line in lines:
    if (line == "<body>"):
      break
  else:
    raise RuntimeError("<body> line not found.")
  out.write(raw_header_1)
  out.write(title)
  out.write(raw_header_2)
  for line in lines:
    if (   line == "</body>"
        or line == '<hr class="docutils footer" />'):
      break
    if (line.startswith('<div class="image">')):
      print >> out, line
      continue
    if (line.startswith('<h1 class="title">')):
      continue
    if (line.startswith("<div ")):
      continue
    if (line == "</div>"):
      continue
    modify_hi = False
    if (line.startswith("<h1>")):
      assert line.endswith("</a></h1>")
      modify_hi = True
    elif (line.startswith("<h2>")):
      assert line.endswith("</a></h2>")
      modify_hi = True
    if (modify_hi):
      line = line[:-9]
      line = line[line.rfind(">")+1:]
      line = "<P><H5><U><B>%s</B></U></H5><P>" % line
    elif (   line.startswith("<ul ")
          or line.startswith("<ol ")):
      line = line[:3]+">"
    print >> out, line
  else:
    raise RuntimeError("</body> line not found.")
  out.write(raw_footer)

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
  tmp_dir = op.join(html_dir, "tmp_files")
  if (not op.isdir(raw_dir)) :
    os.makedirs(raw_dir)
  if (not op.isdir(tmp_dir)) :
    os.makedirs(tmp_dir)
  sys.path.append(os.path.join(html_dir, "scripts")) # XXX gross!
  # FIXME these need to go away
  import create_refinement_txt
  import create_phenix_maps
  import create_model_vs_data_txt
  os.chdir(html_dir)
  top_dir = os.path.dirname(html_dir)
  docs_dir = os.path.join(top_dir, "doc")
  print >> out, "Building PHENIX documentation in %s" % html_dir
  print >> out, "The complete documentation will be in:"
  print >> out, "  %s" % docs_dir
  print >> out, "  creating restructured text files"
  os.chdir(rst_dir)
  create_refinement_txt.run()
  create_phenix_maps.run()
  create_model_vs_data_txt.run()
  os.chdir(rst_dir)
  for module_name, rst_file in create_rst_from_modules :
    print >> out, "    %s" % rst_file
    legend = import_python_object(
      import_path=module_name+".legend",
      error_prefix="",
      target_must_be="",
      where_str="").object
    open(op.join(rst_dir, "reference", rst_file), "w").write(legend)
  print >> out, "  building HTML files from restructured text files"
  if (not params.force) :
    print >> out, \
      "      processing modified files only (override with --force)"
  rst_files = []
  for dirname, dirnames, filenames in os.walk(rst_dir) :
    base_dir = os.path.basename(dirname)
    for file_name in filenames :
      relative_path = file_name
      if (base_dir != "rst_files") :
        relative_path = op.join(base_dir, file_name)
        if (not op.exists(op.join(raw_dir, base_dir))) :
          os.makedirs(op.join(raw_dir, base_dir))
      if file_name.endswith(".txt") :
        rst_files.append(relative_path)
  html_files = []
  def _cmp_make(f1, f2):
    if os.stat(f1).st_mtime < os.stat(f2).st_mtime: return 1
    return -1
  rst_files.sort(_cmp_make)
  for file_name in rst_files:
    assert file_name.endswith(".txt")
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
      html_files.append(html_name)
  print >> out, "  converting restructured text HTML files to raw HTML files"
  for file_name in html_files :
    dirname = op.dirname(file_name)
    raw_file = op.splitext(file_name)[0] + ".raw"
    #print >> out, "    converting %s to %s" % (os.path.basename(file_name),
    #  raw_file)
    f = open(op.join(raw_dir, raw_file), "w")
    raw_from_rst_html(file_name, dirname=dirname, out=f)
    f.close()
    os.remove(file_name)
  print >> out, \
    "  converting raw HTML files, creating tables-of-contents, and indexing"
  os.chdir(tmp_dir)
  toc_and_index.run(args=[html_dir], out=log)
  assert os.path.isfile("phenix_index.htm")
  print >> out, "  populating documentation directory %s" % docs_dir
  if (os.path.exists(docs_dir)) :
    shutil.rmtree(docs_dir)
  os.makedirs(docs_dir)
  shutil.copytree(os.path.join(html_dir, "icons"),
                  os.path.join(docs_dir, "icons"))
  shutil.copytree(os.path.join(html_dir, "images"),
                  os.path.join(docs_dir, "images"))
  for dirname, dirnames, filenames in os.walk(tmp_dir) :
    base_dir = os.path.basename(dirname)
    for file_name in filenames :
      if file_name.endswith(".htm") or file_name.endswith(".html") :
        file_path = file_name
        dest_path = docs_dir
        # enable one additional directory level
        if (base_dir != "tmp_files") :
          file_path = op.join(base_dir, file_name)
          dest_path = op.join(docs_dir, base_dir)
          if (not op.isdir(dest_path)) :
            os.makedirs(dest_path)
        shutil.copy(file_path, dest_path)
  shutil.copy(op.join(html_dir, "phenix_documentation.html"), docs_dir)
  print >> out, "  making symlinks in subdirectories"
  for dirname, dirnames, filenames in os.walk(rst_dir) :
    for dir_name in dirnames :
      dest_path = op.join(docs_dir, dir_name)
      if op.isdir(dest_path) :
        if (sys.platform == "win32") :
          shutil.copytree(op.join(docs_dir, "icons"),
                          op.join(dest_path, "icons"))
          shutil.copytree(op.join(docs_dir, "images"),
                          op.join(dest_path, "images"))
        else :
          os.symlink(op.join(docs_dir, "icons"), op.join(dest_path, "icons"))
          os.symlink(op.join(docs_dir, "images"), op.join(dest_path, "images"))
  os.chdir(docs_dir)
  phenix_version = os.environ.get("PHENIX_VERSION", None)
  release_tag = os.environ.get("PHENIX_RELEASE_TAG", None)
  if (None in [phenix_version, release_tag]) :
    version = "unknown (built %s)" % time.strftime("%b %d %Y", time.localtime())
  else :
    version = "%s-%s" % (phenix_version, release_tag)
  def set_installed_version (file_name) :
    html_in = open(file_name).readlines()
    html_out = open(file_name, "w")
    for line in html_in :
      if ("INSTALLED_VERSION" in line) :
        print >> html_out, re.sub("INSTALLED_VERSION", version, line)
      else :
        print >> html_out, line
  set_installed_version("phenix_documentation.html")
  set_installed_version(op.join("reference", "index.htm"))
  if (sys.platform == "win32") :
    shutil.copy("phenix_documentation.html", "index.html")
  else :
    os.symlink("phenix_documentation.html", "index.html")

if (__name__ == "__main__") :
  run(args=sys.argv[1:])
