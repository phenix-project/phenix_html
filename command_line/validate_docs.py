import os, sys
import libtbx.load_env

elbow_repository_dir = os.path.dirname(libtbx.env.dist_path("elbow"))
phenix_html_dir = os.path.join(elbow_repository_dir, "phenix_html")
doc_dir = os.path.join(elbow_repository_dir, "doc")

def get_image_filenames():
  tmp = []
  for filename in os.listdir(os.path.join(phenix_html_dir, "images")):
    if filename.find(".svn")>-1: continue
    tmp.append(filename)
  return tmp

def get_html_filenames():
  tmp = []
  for cdir, dirs, filenames in os.walk(doc_dir):
    if cdir.find(".svn")>-1: continue
    for filename in filenames:
      if filename.find(".htm")==-1: continue
      if filename.endswith("~"): continue
      tmp.append(os.path.join(cdir, filename))
  return tmp

def get_unused_files(image_files):
  for cdir, dirs, filenames in os.walk(doc_dir):
    if cdir.find(".svn")>-1: continue
    for filename in filenames:
      if filename.find(".htm")==-1: continue
      if filename.endswith("~"): continue
      f=file(os.path.join(cdir, filename), "rb")
      lines = f.read()
      f.close()
      remove = []
      for i, image_file in enumerate(image_files):
        image_file = os.path.join(doc_dir, image_file)
        image_file = os.path.basename(image_file)
        if lines.find(image_file)>-1:
          remove.append(i)
      if remove:
        remove.reverse()
        for r in remove:
          del image_files[r]
  return image_files

def generate_links(lines):
  start = 0
  while lines.find("<a", start)!=-1:
    b = lines.find("<a", start)
    e = lines.find("</a>", start)
    aa = lines[b:e+4]
    start = e+4
    if not aa: break
    if aa.find("href")==-1: continue
    link = aa[aa.find("href"):]
    link = link.split('"')[1]
    if link.find("http:")>-1: continue
    if link.find("#")>-1:
      link = link.split("#")[0]
    if link.find(".htm")==0: continue
    yield link
    start = e+4

def parse_links(filename):
  f=file(filename, "rb")
  lines = f.read()
  f.close()
  links = []
  for link in generate_links(lines):
    if link.find(".htm")==-1: continue
    links.append(link)
  return links

def check_for_eroneous_links(html_files=None):
  for i, html_file in enumerate(html_files):
    html_files[i] = html_file.replace("%s/" % doc_dir, "")
  tmp = {}
  for filename in html_files:
    links = parse_links(os.path.join(doc_dir,filename))
    tmp[filename]=links

  errors = {}
  for key in tmp:
    links = tmp[key]
    abs_key = os.path.join(doc_dir, key)
    assert os.path.exists(abs_key)
    key_dir = os.path.dirname(abs_key)
    for link in tmp[key]:
      abs_link = os.path.join(key_dir, link)
      abs_link = os.path.abspath(abs_link)
      rel_link = abs_link.replace("%s/" % doc_dir, "")
      if rel_link not in html_files:
        errors.setdefault(key, [])
        errors[key].append(abs_link)
  return errors

def run():
  html_files = get_html_filenames()
  errors = check_for_eroneous_links(html_files)
  for filename in errors:
    print "\n  Filename %s has erroneous links to" % filename
    for link in errors[filename]:
      print "    %s" % link
  #
  image_files = get_image_filenames()
  image_files = get_unused_files(image_files)
  print "\n\nImages files not used"
  for i, image_file in enumerate(image_files):
    print "  %2d : %s" % (i+1, image_file)
  html_files = get_unused_files(html_files)
  print "\n\nHTML files not used"
  for i, html_file in enumerate(html_files):
    print "  %2d : %s" % (i+1, html_file)

if __name__=="__main__":
  args = sys.argv[1:]
  del sys.argv[1:]
  run(*tuple(args))
