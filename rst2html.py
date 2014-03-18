"""Generate TOC from header tags.

Ian Rees, 2014

"""
import os
import sys
import tempfile
import argparse
import collections
import re
import codecs

import docutils.core
import xml.dom.minidom
import xml.etree.ElementTree as ET

import iotbx
import iotbx.phil
import libtbx.utils

def merge_indexes(indexes, cutoff=10):
  """Merged indexes."""
  merged = collections.defaultdict(set)
  # Number of times a word appears
  appeared = collections.defaultdict(int) 
  for filename, index in indexes.items():
    for keyword, locations in index.items():
      for location in locations:
        merged[keyword].add('%s/%s'%(filename, location))
  return merged

class FormatCitation(object):
  def __init__(self, citation):
    self.citation = citation
    
  def format(self):
    return "Citation: %s"%self.citation

class FormatPHIL(object):
  def __init__(self, command):
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

    if isinstance(master_params, libtbx.phil.scope):
      pass
    elif isinstance(master_params, (str, unicode)):
      master_params = iotbx.phil.parse(master_params, process_includes=True)
    elif hasattr(master_params, '__call__'):
      master_params = master_params()
    else:
      pass
    
    if not master_params:
      raise Exception("No PHIL command found.")
    self.master_params = master_params

  def format(self):
    return ET.tostring(self._walk())

  def _walk_elem(self, param, depth=0, parent=None, cls='phil-param'):
    elem = ET.SubElement(parent, 'li', attrib={'class':cls})
    span = ET.SubElement(elem, 'span', attrib={'cls':'phil-name'})
    span.text = str(param.name)
    try:
      param.words
      words = ET.SubElement(elem, 'span', attrib={'cls':'phil-words'})
      words.text = " = " + " ".join([str(i) for i in param.words])
    except:
      pass
    if param.help:
      help = ET.SubElement(elem, 'span', attrib={'cls':'phil-help'})
      help.text = str(param.help)
    return elem
    
  def _walk(self, params=None, depth=0, parent=None):
    params = params or self.master_params
    if parent is None:
      parent = ET.Element('ul')
    values = []
    objects = []
    res = params.objects
    for i in res:
      try:
        x, y = i.name, i.type
        values.append(i)
      except:
        objects.append(i)
    for i in values:
      elem = self._walk_elem(i, depth=depth, parent=parent, cls='phil-param')
    for i in objects:
      elem = self._walk_elem(i, depth=depth, parent=parent, cls='phil-scope')
      np = ET.SubElement(elem, 'ul')
      self._walk(i, depth=depth+1, parent=np)
    return parent
  
class PublishRST(object):
  """Convert RST to HTML."""
  TAG_RE = re.compile("""({{(?P<tag>.+?):(?P<command>.+?)}})""")  
  KEYWORDS_RE = re.compile("""(\w+)""")
    
  def __init__(self, filename):
    """Filename is RST .txt file."""
    self.filename = filename
    self.doc = None
    self.data = None
    with codecs.open(self.filename, 'r', 'utf-8') as f:
      self.data = f.read()

  def render(self):
    """Convert RST to HTML, process all tags."""
    doc = docutils.core.publish_string(self.data, writer_name='html')
    for tag in self.TAG_RE.finditer(doc):
      doc = self._render_tag(tag.groups()[0], tag.group('tag'), tag.group('command'), doc)
    self.doc = doc
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
    dom = ET.fromstring(self.doc.encode('utf-8'))
    for elem in dom.findall(""".//{http://www.w3.org/1999/xhtml}div[@class='section']"""):
      for child in elem.findall(""".//"""):
        for keyword in self._keywords(child.text):
          index[keyword.lower()].add(elem.attrib['id'])
    return index
  
  def _keywords(self, text):
    if text is None:
      return set()
    words = self.KEYWORDS_RE.findall(text)
    return set(words)
          
if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("filenames", help="Filenames", nargs='+')
  args = parser.parse_args()

  for filename in args.filenames:
    publish = PublishRST(filename)
    doc = publish.render()
    index = publish.index()
    for k,v in index.items():
      print k, v
    