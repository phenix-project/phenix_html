"""Convert PHENIX reStructuredText files to HTML

This includes PHIL documentaiton and citations.

Ian Rees, 2014

"""
from __future__ import division
import os
import os.path as op
import sys
import shutil
import collections
import re
import codecs

import docutils.core
import xml.etree.ElementTree as ET

import phenix.utilities.citations
import iotbx.phil
import libtbx.load_env
import libtbx.utils

HTML_PATH = libtbx.env.find_in_repositories(relative_path="phenix_html")
if HTML_PATH is None:
  raise Sorry("Could not find phenix_html.")

def replace_phenix_version (doc) :
  base_version = os.environ.get("PHENIX_VERSION")
  release_tag = os.environ.get("PHENIX_RELEASE_TAG")
  if (base_version is None) :
    version = "unknown"
  else :
    assert (release_tag is not None)
    version = "%s-%s" % (base_version, release_tag)
  return doc.replace("INSTALLED_VERSION", version)

class FormatCitation(object):
  """Format a citation as HTML."""
  
  def __init__(self, citation):
    self.citation = citation

  def format(self):
    return phenix.utilities.citations.format_citation_html(self.citation)

class FormatPHIL(object):
  """Format PHIL as HTML."""
  
  def __init__(self, command):
    """Command is a PHENIX command, e.g. phenix.refine"""
    # Search the module for the following attributes:
    search = ["master_params", "master_phil", "master_params_str", "master_phil_str", "get_master_phil"]
    master_params = None
    for i in search:
      try:
        master_params = libtbx.utils.import_python_object(
          import_path='%s.%s'%(command, i),
          error_prefix="",
          target_must_be="",
          where_str="").object
        break
      except Exception, e:
        pass

    # Check if the module attribute is a string, a scope, ...
    if isinstance(master_params, libtbx.phil.scope):
      pass
    elif isinstance(master_params, (str, unicode)):
      master_params = iotbx.phil.parse(master_params, process_includes=True)
    elif hasattr(master_params, '__call__'):
      master_params = master_params()
    else:
      pass

    if not master_params:
      raise Exception("No PHIL command found for %s." % command)
    self.master_params = master_params

  def format(self):
    """Return PHIL scope as HTML."""
    return ET.tostring(self._walk())

  def _walk_elem(self, param, depth=0, parent=None, cls='phil-param'):
    """Create element from PHIL param. cls are the CSS classes."""
    elem = ET.SubElement(parent, 'li', attrib={'class': cls, 'data-expert':str(param.expert_level or 0)})
    span = ET.SubElement(elem, 'span', attrib={'class':'phil-name'})
    span.text = str(param.name)
    try:
      param.words
      words = ET.SubElement(elem, 'span', attrib={'class':'phil-words'})
      words.text = " = " + " ".join([str(i) for i in param.words]) + " "
    except Exception, e:
      pass
    if param.help:
      help = ET.SubElement(elem, 'span', attrib={'class':'phil-help'})
      help.text = str(param.help)
    return elem

  def _walk(self, params=None, depth=0, parent=None):
    """Walk PHIL nodes. Returns an ElementTree element."""
    params = params or self.master_params
    if parent is None:
      parent = ET.Element('ul', attrib={'class':'phil'})
    # ... check if param or scope.
    values = []
    objects = []
    res = params.objects
    for i in res:
      try:
        x, y = i.name, i.type
        values.append(i)
      except Exception, e:
        objects.append(i)
    # Leaf elements for params.
    for i in values:
      elem = self._walk_elem(i, depth=depth, parent=parent, cls='phil-param')
    # A nested ul element for scopes.
    for i in objects:
      elem = self._walk_elem(i, depth=depth, parent=parent, cls='phil-param phil-scope')
      np = ET.SubElement(elem, 'ul')
      self._walk(i, depth=depth+1, parent=np)
    return parent

class PublishRST(object):
  """Convert RST to HTML."""
  # Regular expressions for parsing {{tags}} and keywords.
  TAG_RE = re.compile("""({{(?P<tag>.+?):(?P<command>.+?)}})""")
  KEYWORDS_RE = re.compile("""([a-zA-Z]{3,})""")

  def __init__(self, filename, ignore_tags=False):
    """Filename is RST .txt file."""
    self.filename = filename
    self.doc = None
    self.data = None
    self.ignore_tags = ignore_tags
    with codecs.open(self.filename, 'r', 'utf-8') as f:
      self.data = f.read()

  def render(self):
    """Return RST as HTML and process {{tags}}."""
    template = os.path.join(HTML_PATH, 'template.html')
    doc = docutils.core.publish_string(self.data, writer_name='html', settings_overrides={'template':template})
    # Process tags.
    if not self.ignore_tags:
      for tag in self.TAG_RE.finditer(doc):
        doc = self._render_tag(tag.groups()[0], tag.group('tag'), tag.group('command'), doc)
    self.doc = replace_phenix_version(doc)
    return self.doc

  def _render_tag(self, sub, tag, command, doc):
    """Process a {{tag:command}}."""
    result = ""
    if tag == 'phil':
      result = FormatPHIL(command).format()
    elif tag == 'citation':
      result = FormatCitation(command).format()
    return re.sub(sub, result, doc)

  def index(self):
    """Create index."""
    index = collections.defaultdict(set)
    # Parse with ElementTree so we can find all text nodes.
    try:
      dom = ET.fromstring(self.doc)
    except Exception, e:
      print "Couldn't index: %s"%e
      return index

    # xml.ElementTree uses XML-style namespaced tags.
    for elem in dom.findall(""".//{http://www.w3.org/1999/xhtml}div[@class='section']"""):
      for child in elem.findall(""".//"""):
        for keyword in self._keywords(child.text):
          index[keyword.lower()].add(elem.attrib['id'])
    return index

  def _keywords(self, text):
    """Parse keywords from string."""
    if text is None:
      return set()
    return set(self.KEYWORDS_RE.findall(text))

class FormatIndex(object):
  """Index page."""
  # TODO: Maybe this should take list of PublishRST instances
  #   instead of dict of their index() results.
  
  def __init__(self, indexes):
    """Indexes is key: filename, value: PublishRST.index()"""
    self.indexes = indexes
    # Maximum occurrences of a term.
    self.cutoff = 10
    # List of words to ignore in index.
    self.reject = set([])
    with open(os.path.join(HTML_PATH, 'lib', 'reject')) as f:
      self.reject = set([i.strip() for i in f.readlines()])

  def render(self):
    """Return HTML formatted index page."""
    merged = self.merge_indexes(self.indexes, cutoff=self.cutoff)
    with open(os.path.join(HTML_PATH, 'template.html')) as f:
      template = f.read()
    return template%{
      'head':"""<title>Index</title>""",
      'html_body':ET.tostring(self._format(merged))
    }

  def _format(self, merged):
    """Return ul element with nested ul's for each index term."""
    parent = ET.Element('ul', attrib={'class':'phenix-index'})
    for keyword, references in sorted(merged.items()):
      elem = ET.SubElement(parent, 'li')
      elem.text = str(keyword).encode('utf-8')
      child = ET.SubElement(elem, 'ul')
      for reference in sorted(references):
        ref = ET.SubElement(child, 'li')
        a = ET.SubElement(ref, 'a', attrib={'href':reference})
        a.text = str(reference)
    return parent

  def merge_indexes(self, indexes, cutoff=10):
    """Return the merged index. Cutoff is the max number of times a word may appear."""
    merged = collections.defaultdict(set)
    for filename, index in indexes.items():
      for keyword, locations in index.items():
        for location in locations:
          merged[keyword].add('%s#%s'%(filename, location))
    # Filter result.
    for word in set(merged.keys()) & self.reject:
      del merged[word]
    for word in merged.keys():
      if len(merged[word]) > cutoff:
        del merged[word]
    return merged

class FormatOverview(object):
  """Format PHENIX Overview page."""

  def __init__(self):
    pass

  def render(self):
    """Return HTML formatted overview page."""
    with open(os.path.join(HTML_PATH, 'phenix_documentation.html')) as f:
      doc = f.read()
    doc = replace_phenix_version(doc)
    with open(os.path.join(HTML_PATH, 'template.html')) as f:
      template = f.read()
    return template%{
      'head': """<title>PHENIX Documentation</title>""",
      'html_body': doc
    }

#######################################

# FIXME ignore_errors should be False once we fix remaining issues...
master_phil_str = """
clean = False
  .type = bool
  .help = Delete the entire docs directory and re-populate.
ignore_errors = True
  .type = bool
  .help = Don't crash on errors in RST processing.
"""

create_rst_from_modules = [
  ("mmtbx.command_line.reciprocal_space_arrays","reciprocal_space_arrays.txt"),
  ("mmtbx.command_line.map_value_at_point", "map_value_at_point.txt"),
  ("mmtbx.command_line.fmodel", "fmodel.txt"),
]

def replace_tree (src_path, dest_path) :
  if op.exists(dest_path) :
    shutil.rmtree(dest_path)
  shutil.copytree(src_path, dest_path)

def link_tree (src_path, dest_path) :
  if (sys.platform == "win32") :
    if op.isdir(dest_path) :
      shutil.rmtree(dest_path)
    replace_tree(src_path, dest_path)
  else :
    if op.exists(dest_path) :
      os.remove(dest_path)
    os.symlink(src_path, dest_path)

# FIXME this is really not a good idea - except for the citations, which
# do actually change regularly
def auto_generate_rst_files (out) :
  sys.path.append(os.path.join(HTML_PATH, "scripts"))
  import create_refinement_txt
  import create_phenix_maps
  import create_model_vs_data_txt
  import create_citations_txt
  create_refinement_txt.run()
  create_phenix_maps.run()
  create_model_vs_data_txt.run()
  create_citations_txt.run()
  for module_name, rst_file in create_rst_from_modules :
    print >> out, "    %s" % rst_file
    legend = libtbx.utils.import_python_object(
      import_path=module_name+".legend",
      error_prefix="",
      target_must_be="",
      where_str="").object
    open(op.join("reference", rst_file), "w").write(legend)

def run (args, out=sys.stdout) :
  cmdline = libtbx.phil.command_line.process(
    args=args,
    master_string=master_phil_str)
  params = cmdline.work.extract()
  if (out is None) : out = sys.stdout
  html_dir = libtbx.env.find_in_repositories(
    relative_path="phenix_html",
    test=os.path.isdir)
  if (html_dir is None) :
    raise Sorry("phenix_html repository not found.")
  rst_dir = op.join(html_dir, "rst_files")
  top_dir = os.path.dirname(html_dir)
  docs_dir = os.path.join(top_dir, "doc")
  if op.exists(docs_dir) and params.clean :
    shutil.rmtree(docs_dir)
  if (not op.exists(docs_dir)) :
    os.makedirs(docs_dir)
  print >> out, "Building PHENIX documentation in %s" % html_dir
  print >> out, "The complete documentation will be in:"
  print >> out, "  %s" % docs_dir
  print >> out, "  creating restructured text files"
  os.chdir(rst_dir)
  auto_generate_rst_files(out=out)
  os.chdir(rst_dir)
  indexes = {}
  print >> out, "  building HTML files from restructured text files"
  rst_files = []
  for dirname, dirnames, filenames in os.walk(rst_dir) :
    base_dir = os.path.basename(dirname)
    for file_name in filenames :
      relative_path = file_name
      dest_path = docs_dir
      if (base_dir != "rst_files") :
        relative_path = op.join(base_dir, file_name)
        dest_path = op.join(docs_dir, base_dir)
        if (not op.exists(dest_path)) :
          os.makedirs(dest_path)
      if file_name.endswith(".txt") :
        outfile = "%s.html" % op.basename(file_name).rpartition(".")[0]
        out_url = outfile
        if (base_dir != "rst_files") :
          out_url = op.join(base_dir, out_url)
        out_path = op.join(dest_path, outfile)
        print >> out, "    converting %s to %s" % (file_name, outfile)
        try:
          publish = PublishRST(relative_path,
            ignore_tags=(file_name == "doc_procedures.txt"))
          doc = publish.render()
          indexes[out_url] = publish.index()
        except Exception, e:
          if (not params.ignore_errors) :
            raise
          print "      error: %s" % e
        else :
          with open(out_path, "w") as f:
            f.write(doc)
  os.chdir(docs_dir)
  with open("phenix_index.html", "w") as f:
    f.write(FormatIndex(indexes).render())
  with open("index.html", "w") as f:
    f.write(FormatOverview().render())
  print >> out, "  copying images"
  replace_tree(os.path.join(html_dir, "icons"),
               os.path.join(docs_dir, "icons"))
  replace_tree(os.path.join(html_dir, "images"),
               os.path.join(docs_dir, "images"))
  replace_tree(os.path.join(html_dir, "css"),
               os.path.join(docs_dir, "css"))
  print >> out, "  making symlinks in subdirectories"
  for dirname, dirnames, filenames in os.walk(rst_dir) :
    for dir_name in dirnames :
      dest_path = op.join(docs_dir, dir_name)
      if op.isdir(dest_path) :
        link_tree(op.join(docs_dir, "icons"), op.join(dest_path, "icons"))
        link_tree(op.join(docs_dir, "images"), op.join(dest_path, "images"))
        link_tree(op.join(docs_dir, "css"), op.join(dest_path, "css"))

if (__name__ == "__main__") :
  run(sys.argv[1:])
