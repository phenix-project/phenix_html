"""Convert PHENIX raw html fragments to reStructuredText.

Ian Rees, 2014

"""

from __future__ import division
import subprocess
import argparse
import os
import re

# Docutils
import docutils.core
# HTML Tidy
import tidylib

def convert(filename):
  """Convert raw html fragment in filename to rst.

  This will create a number of files:
      filename.debug            Pre-cleaned HTML
      filename.clean.html       HTML Tidy cleaned HTML
      filename.txt              Pandoc-converted RST (main output)
      filename.txt.html         docutils RST -> HTML

  Pandoc (command) and tidylib (module) are required dependencies.
  """
  with open(filename) as f:
    data = f.read()

  print "\n=====", filename
  filename = os.path.basename(filename)
  filename = filename.rpartition(".")[0]
  prefile = '%s.debug'%filename
  outfile = '%s.clean.html'%filename
  rstfile = '%s.txt'%filename
  rsthtmlfile = '%s.txt.html'%filename

  # Replace PHENIX comments; these are malformed (missing "-->")
  data = """<html><body>%s</html></body>"""%data
  data = re.sub("""(<!--(\s+)?REMARK PHENIX TITLE START(.*?>)?)""", "", data, flags=re.DOTALL)
  data = re.sub("""(<!--(\s+)?REMARK PHENIX BODY START(.*?>)?)""", "", data, flags=re.DOTALL)

  # Kill all styles.
  data = re.sub("""style=".+?"(\s+)?""", "", data, flags=re.I)
  data = re.sub("""class="literal-block"(\s+)?""", "", data, flags=re.I)

  # Kill alt=, because it breaks pandoc. They're not used anyways.
  data = re.sub("""alt=".+?"(\s+)?""", "", data, flags=re.I)

  # Remove empty pre's; these produce invalid RST.
  data = re.sub("""<pre.+?>\s+</pre>""", "", data, flags=re.I | re.DOTALL)

  # Convert h4 to h1, h5 to h2 for proper RST conversion.
  data = re.sub("""<h4>""", "<h1>", data, flags=re.I)
  data = re.sub("""</h4>""", "</h1>", data, flags=re.I)
  data = re.sub("""<h5>""", "<h2>", data, flags=re.I)
  data = re.sub("""</h5>""", "</h2>", data, flags=re.I)

  # The many unclosed <ul> tags are not handled well by tidy...
  # it actually works better if we just remove them all, and let tidy
  # create them from scratch around <li>'s.
  data = re.sub("""<ol>""", "", data, flags=re.I)
  data = re.sub("""<ul>""", "", data, flags=re.I)
  # ... leave the </ul> because it clears some unclosed li's.
  # data = re.sub("""</UL>""", "", data, flags=re.I)

  # Write debugging output.
  with open(prefile, 'w') as f:
    f.write(data)

  # Clean with HTML Tidy and write output.
  doc, e = tidylib.tidy_document(data)
  cleaned = str(doc)
  with open(outfile, 'w') as f:
    f.write(cleaned.encode('utf-8'))

  # Convert to RST using Pandoc
  subprocess.check_call(['pandoc', '-s', outfile, '-t', 'rst', '-o', rstfile])
  subprocess.check_call(['pandoc', '-s', rstfile, '-t', 'html', '-o', rsthtmlfile])

  # Open RST and convert to HTML using docutils
  with open(rstfile) as f:
    doc = f.read()

  # Write HTML output.
  doc = docutils.core.publish_string(doc, writer_name='html')
  with open(rsthtmlfile, 'w') as f:
    f.write(doc)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("filenames", help="Filenames", nargs='+')
  args = parser.parse_args()
  for filename in args.filenames:
    convert(filename)
