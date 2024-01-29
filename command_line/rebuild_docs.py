"""Convert Phenix reStructuredText files to HTML

This includes PHIL documentaiton and citations.

"""
from __future__ import division
from __future__ import print_function
import os
import os.path as op
import sys
import shutil
import collections
import re
import codecs

import docutils.core
import xml.etree.ElementTree as ET

import libtbx.citations
from phenix import phenix_info
import iotbx.phil
import libtbx.load_env
import libtbx.utils

from libtbx.utils import to_str

# XXX it would be better not to set this globally if possible...
HTML_PATH = libtbx.env.find_in_repositories(relative_path="phenix_html")
if HTML_PATH is None:
  raise libtbx.utils.Sorry("Could not find phenix_html.")

def replace_phenix_version (doc) :
  base_version, release_tag = phenix_info.version_and_release_tag()
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
    return libtbx.citations.format_citation_doc(self.citation)

class FormatPHIL(object):
  """Format PHIL as HTML."""

  def __init__(self, command):
    """Command is a Phenix command, e.g. phenix.refine"""
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
      except Exception as e:
        pass

    # try ProgramTemplate location
    if master_params is None:
      try:
        module = libtbx.utils.import_python_object(
        import_path='%s' % command,
        error_prefix="",
        target_must_be="",
        where_str="").object
        master_params = module.master_phil_str
      except Exception:
        pass

    # Check if the module attribute is a string, a scope, ...
    if (sys.version_info.major == 2 and isinstance(master_params, (str, unicode))) \
      or isinstance(master_params, str):
      master_params = iotbx.phil.parse(master_params, process_includes=True)
    elif hasattr(master_params, '__call__'):
      master_params = master_params()
    assert isinstance(master_params, libtbx.phil.scope)

    if not master_params:
      raise Exception("No PHIL command found for %s." % command)
    self.master_params = master_params

  def format(self):
    """Return PHIL scope as HTML."""
    return to_str(ET.tostring(self._walk()))

  def _walk_elem(self, param, depth=0, parent=None, cls='phil-param'):
    """Create element from PHIL param. cls are the CSS classes."""
    elem = ET.SubElement(parent, 'li', attrib={'class': cls, 'data-expert':str(param.expert_level or 0)})
    span = ET.SubElement(elem, 'span', attrib={'class':'phil-name'})
    span.text = str(param.name)
    try:
      param.words
      words = ET.SubElement(elem, 'span', attrib={'class':'phil-words'})
      words.text = " = " + " ".join([str(i) for i in param.words]) + " "
    except Exception as e:
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
      except Exception as e:
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

class Publish(object):
  # Regular expressions for parsing {{tags}} and keywords.
  TAG_RE = re.compile(r"""({{(?P<tag>\w*)(:)?(?P<command>.+?)?}})""")
  KEYWORDS_RE = re.compile(r"""([a-zA-Z]{3,})""")

  # Render interface, tags
  def render(self, root=''):
    return ''

  def _render_tags(self, doc, root=''):
    doc = to_str(doc)
    for match in self.TAG_RE.finditer(doc):
      sub = match.groups()[0]
      tag = match.group('tag')
      command = match.group('command')
      # print "Rendering tag:", sub, tag, command
      result = ""
      try:
        if tag == 'phil':
          result = FormatPHIL(command).format()
        elif tag == 'citation':
          result = FormatCitation(command).format()
        elif tag == 'root':
          result = root
        elif tag == 'anchor' :
          result = """<a name="%s"/>""" % command
      except Exception as e:
        print("Error with tag:", e)
      else:
        # print "...result:", result
        doc = re.sub(sub, result, doc)
    return doc

class PublishRST(Publish):
  """Convert RST to HTML."""

  def __init__(self, filename):
    """Filename is RST .txt file."""
    self.filename = filename
    self.doc = None
    self.data = None
    if sys.version_info[0] == 2:
      with codecs.open(self.filename, 'r', encoding='utf-8') as f:
        self.data = f.read()
    else:
      with open(self.filename, 'r') as f:
        self.data = f.read()

  def render(self, root=''):
    """Return RST as HTML and process {{tags}}."""
    template = os.path.join(HTML_PATH, 'template.html')
    doc = docutils.core.publish_string(self.data, writer_name='html', settings_overrides={'template':template})
    # Process tags.
    doc = self._render_tags(doc, root=root)
    self.doc = replace_phenix_version(doc)
    self.doc = to_str(self.doc)
    return self.doc

  def index(self):
    """Create index."""
    index = collections.defaultdict(set)
    # Parse with ElementTree so we can find all text nodes.
    try:
      dom = ET.fromstring(self.doc)
    except Exception as e:
      print("Couldn't index: %s"%e)
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
    return set(self.KEYWORDS_RE.findall(to_str(text)))

class FormatIndex(Publish):
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

  def render(self, root=''):
    """Return HTML formatted index page."""
    merged = self.merge_indexes(self.indexes, cutoff=self.cutoff)
    with open(os.path.join(HTML_PATH, 'template.html')) as f:
      template = f.read()
    doc = template%{
      'head':"""<title>Index</title>""",
      'html_body':ET.tostring(self._format(merged)),
      'root': ''
    }
    doc = self._render_tags(doc, root=root)
    return doc

  def _format(self, merged):
    """Return ul element with nested ul's for each index term."""
    parent = ET.Element('ul', attrib={'class':'phenix-index'})
    for keyword, references in sorted(merged.items()):
      elem = ET.SubElement(parent, 'li')
      elem.text = to_str(keyword)
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
    for word in list(merged.keys()):
      if len(merged[word]) > cutoff:
        del merged[word]
    return merged

class FormatOverview(Publish):
  """Format Phenix Overview page."""
  def render(self, root=''):
    """Return HTML formatted overview page."""
    with open(os.path.join(HTML_PATH, 'phenix_documentation.html')) as f:
      doc = f.read()
    doc = replace_phenix_version(doc)
    with open(os.path.join(HTML_PATH, 'template.html')) as f:
      template = f.read()
    doc = template%{
      'head': """<title>Phenix Documentation</title>""",
      'html_body': doc,
      'root': ''
    }
    doc = self._render_tags(doc, root=root)
    return doc

#######################################

# FIXME ignore_errors should be False once we fix remaining issues...
master_phil_str = """
clean = False
  .type = bool
  .help = Delete the entire docs directory and re-populate.
ignore_errors = True
  .type = bool
  .help = Don't crash on errors in RST processing.
process_all_files = False
  .type = bool
  .help = If False, only process .txt files that have been modified.
top_dir = None
  .type = path
  .help = Use a different directory tree for doc generation
"""

create_rst_from_modules = [
  ("mmtbx.command_line.reciprocal_space_arrays","reciprocal_space_arrays.txt"),
  ("phenix.programs.map_value_at_point", "map_value_at_point.txt"),
#  ("mmtbx.command_line.fmodel", "fmodel.txt"),
]

def replace_tree (src_path, dest_path):
  if os.path.exists(dest_path) :
    shutil.rmtree(dest_path)
  shutil.copytree(src_path, dest_path)

def link_tree(src_path, dest_path):
  if (sys.platform == "win32") :
    if os.path.isdir(dest_path) :
      shutil.rmtree(dest_path)
    replace_tree(src_path, dest_path)
  else :
    if os.path.exists(dest_path) :
      os.remove(dest_path)
    os.symlink(src_path, dest_path)

# FIXME this is really not a good idea - except for the citations, which
# do actually change regularly
def auto_generate_rst_files(out):
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
    print("    %s" % rst_file, file=out)
    legend = libtbx.utils.import_python_object(
      import_path=module_name+".legend",
      error_prefix="",
      target_must_be="",
      where_str="").object
    open(os.path.join("reference", rst_file), "w").write(legend)

def run (args, out=sys.stdout) :
  global HTML_PATH
  global create_rst_from_modules
  cmdline = libtbx.phil.command_line.process(
    args=args,
    master_string=master_phil_str)
  params = cmdline.work.extract()
  if (out is None):
    out = sys.stdout

  # Checked for HTML_PATH at module load.
  # Start converting all RST .txt to .html.
  top_dir = os.path.dirname(HTML_PATH)
  rst_dir = os.path.join(HTML_PATH, "rst_files")
  docs_dir = libtbx.env.under_root('doc')
  if libtbx.env.installed:
    docs_dir = os.path.join(libtbx.env.under_root('phenix'), 'doc')
  if params.top_dir:
    top_dir = os.path.abspath(params.top_dir)
    rst_dir = os.path.join(top_dir, "rst_files")
    create_rst_from_modules = []
    print('resetting top directory to %s' % top_dir)
    docs_dir = os.path.join(top_dir, 'doc')
    print('resetting doc directory to %s' % top_dir)
    HTML_PATH = top_dir
  if os.path.exists(docs_dir) and params.clean:
    shutil.rmtree(docs_dir)
  if (not os.path.exists(docs_dir)):
    os.makedirs(docs_dir)

  print("Building Phenix documentation in %s"%top_dir, file=out)
  print("The complete documentation will be in:", file=out)
  print("  %s" % docs_dir, file=out)
  print("  creating restructured text files", file=out)
  os.chdir(rst_dir)
  if not params.top_dir: auto_generate_rst_files(out=out)
  os.chdir(rst_dir)

  print("  building HTML files from restructured text files", file=out)
  indexes = {}
  for dirname, dirnames, filenames in os.walk(rst_dir):
    for filename in [x for x in filenames if x.endswith('.txt')]:
      # Some complicated directory relationships.
      # relpath is the directory relative to rst_dir root (for output)
      # root is the inverse (for linking between pages)
      # infile is the actualy input .txt file
      # outpath is the output dir, outname is HTML file name
      # outfile is the joined outpath, outname
      relpath = os.path.relpath(dirname, rst_dir)
      root = os.path.relpath(rst_dir, dirname)
      if root == '.':
        root = ''
      else:
        root = root + '/'
      infile  = os.path.join(dirname, filename)
      outname = "%s.html"%os.path.basename(filename).rpartition(".")[0]
      outpath = os.path.join(docs_dir, relpath)
      outfile = os.path.join(outpath, outname)
      # Check the output directory exists.
      try:
        os.makedirs(outpath)
      except Exception:
        pass

      if not params.process_all_files:
        if os.path.exists(outfile):
          if os.stat(infile).st_mtime<os.stat(outfile).st_mtime: continue

      print("    converting %s to %s" % (infile, outfile), file=out)
      try:
        publish = PublishRST(infile)
        doc = publish.render(root=root)
        # Make sure we index using relative path!
        indexes[os.path.join(relpath, outname)] = publish.index()
      except Exception as e:
        if (not params.ignore_errors):
          raise
        print("      error: %s" % e)
      else :
        if doc.find('system-messages')!=-1:
          raise libtbx.utils.Sorry('''
        Something is wrong with input. Please correct syntax.
        ''')
        with open(outfile, "w") as f:
          f.write(doc)

  if params.top_dir: return
  # Write out the main page, and index page.
  os.chdir(docs_dir)
  with open("phenix_index.html", "w") as f:
    f.write(FormatIndex(indexes).render())
  with open("index.html", "w") as f:
    f.write(FormatOverview().render())

  # Copy images, CSS, etc.
  print("  copying images", file=out)
  replace_tree(op.join(HTML_PATH, "icons"), op.join(docs_dir, "icons"))
  replace_tree(op.join(HTML_PATH, "images"), op.join(docs_dir, "images"))
  replace_tree(op.join(HTML_PATH, "css"), op.join(docs_dir, "css"))

  # Copy extras
  print("  copying extras", file=out)
  replace_tree(op.join(HTML_PATH, 'extras'), op.join(docs_dir, 'extras'))

if (__name__ == "__main__") :
  run(sys.argv[1:])
