import libtbx.load_env
import sys, os

structure_refinement_raw = libtbx.env.find_in_repositories(
  relative_path="phenix_html/rst_files/refinement.pre",
  test=os.path.isfile)

phenix_refine_files = "phenix_html/phenix_refine_files/"

def get_params_file(file_name):
  result = libtbx.env.find_in_repositories(
    relative_path=phenix_refine_files+"%s"%file_name,
    test=os.path.isfile)
  if(result is None):
    print "File %s is not found in %s."%(file_name, phenix_refine_files)
  return result

def inject_file_content(parameter_file_name, ofn, indentation):
  file_name = get_params_file(file_name = parameter_file_name)
  lines = open(file_name).read().splitlines()
  for line in lines:
    if(line.strip() != ""):
      print >> ofn, " "*indentation, line

def find_indentation(line):
  i = 0
  while line[i] != "#": i+=1
  return i-1

def run():
  if(structure_refinement_raw is None):
    print "No refinement.pre file found."
  ofn = open("refinement.txt","w")
  for line in open(structure_refinement_raw).read().splitlines():
    if(line.count("#include_params")):
      start_position = find_indentation(line)
      line = line.split()
      assert len(line) == 2
      inject_file_content(parameter_file_name = line[1],
                          ofn                 = ofn,
                          indentation         = start_position)
    else:
      print >> ofn, line

if (__name__ == "__main__"):
  run()
