
from __future__ import division
from __future__ import print_function
from phenix.utilities import citations
import libtbx.load_env
import os.path as op

def run () :
  html_dir = libtbx.env.find_in_repositories(relative_path="phenix_html")
  rst_file = op.join(html_dir, "rst_files", "reference", "citations.txt")
  f = open(rst_file, "w")
  txt_header = """\
====================================
List of references related to Phenix
====================================

Current primary Phenix citation:
--------------------------------

{{citation:phenix}}

Other articles
--------------

The articles below include both papers produced by members of the Phenix
collaboration, and works by external groups relating to methods used in
Phenix (and elsewhere).

"""
  f.write(txt_header)
  all_articles = sorted(citations.citations_params.citation,
    lambda a,b: cmp(b.year, a.year))
  for citation in all_articles :
    if (citation.article_id != "phenix") :
      # TODO toggle-able article_id fields
      print("{{citation:%s}}" % citation.article_id, file=f)
      print("", file=f)
  f.close()

if (__name__ == "__main__") :
  run()
