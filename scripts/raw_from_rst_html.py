import sys

raw_header = """\
<!--REMARK PHENIX TITLE START  Put your title here>


<H4><U>TITLE</U></H4>


<!--REMARK PHENIX TITLE END-->

<!--REMARK PHENIX BODY START   Put your text here.
Anything enclosed in header html H4 H5 etc will go in the table of contents>
"""

raw_footer = """\
<!--REMARK PHENIX BODY END-->
"""

def run(args):
  assert len(args) == 1
  lines = iter(open(args[0]).read().splitlines())
  for line in lines:
    if (line == "<body>"):
      break
  else:
    raise RuntimeError("<body> line not found.")
  sys.stdout.write(raw_header)
  for line in lines:
    if (   line == "</body>"
        or line == '<hr class="docutils footer" />'):
      break
    if (line.startswith('<div class="image">')):
      print line
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
    print line
  else:
    raise RuntimeError("</body> line not found.")
  sys.stdout.write(raw_footer)

if (__name__ == "__main__"):
  run(sys.argv[1:])
