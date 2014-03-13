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
      tmp.append(filename)
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
        if lines.find(image_file)>-1:
          remove.append(i)
      if remove:
        remove.reverse()
        for r in remove:
          del image_files[r]
  return image_files

def run():
  image_files = get_image_filenames()
  image_files = get_unused_files(image_files)
  print "\n\nImages files not used"
  for i, image_file in enumerate(image_files):
    print "  %2d : %s" % (i+1, image_file)
  html_files = get_html_filenames()
  html_files = get_unused_files(html_files)
  print "\n\nHTML files not used"
  for i, html_file in enumerate(html_files):
    print "  %2d : %s" % (i+1, html_file)

if __name__=="__main__":
  args = sys.argv[1:]
  del sys.argv[1:]
  run(*tuple(args))
