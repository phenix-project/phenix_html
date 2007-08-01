import libtbx.load_env
import sys, os

pdb = libtbx.env.find_in_repositories(
  relative_path="phenix_regression/phenix_doc/enk_doc.pdb",
  test=os.path.isfile)
pdb_o5t = libtbx.env.find_in_repositories(
  relative_path="phenix_regression/phenix_doc/dna_o5t.pdb",
  test=os.path.isfile)
hkl_anom = libtbx.env.find_in_repositories(
  relative_path="phenix_regression/reflection_files/enk_all_anomal.mtz",
  test=os.path.isfile)
hkl = libtbx.env.find_in_repositories(
  relative_path="phenix_regression/reflection_files/enk.mtz",
  test=os.path.isfile)
  
create_structure_refinement_txt = libtbx.env.find_in_repositories(
  relative_path="phenix_html/scripts/create_refinement_txt.py",
  test=os.path.isfile)

def get_full_path(x):
  x_full = libtbx.env.find_in_repositories(
                   relative_path = "phenix_html/phenix_refine_files/%s"%x,
                   test          = os.path.isfile)
  if(x is None):
    print "File not found: ", x
    assert cmd_i is not None
  return x_full

def inject_parameter_file(cmd):
  cmd = cmd.split()
  new_cmd = []
  for cmd_i in cmd:
    if(cmd_i.count(".params")==1 or
       cmd_i.count(".cif")==1 or
       cmd_i.count(".def")==1):
      cmd_i = get_full_path(cmd_i)
    new_cmd.append(cmd_i)
  return " ".join(new_cmd)

def exercise(args):
  dry_run = "--dry_run" in args
  assert create_structure_refinement_txt is not None
  os.system("python %s"%create_structure_refinement_txt)
  dir_cont = os.listdir(".")
  assert "refinement.txt" in dir_cont
  if 1:
     line_start = False
     slash = str("%s"%"\ ").strip()
     pick_next = False
     amp_counter = 0
     cmd_counter = 0
     for st in open("refinement.txt", "r").read().splitlines():
       fake_cmd = ((st.find("<") < 0 or st.find(">") < 0) and
                   (st.find("[") < 0 or st.find("]") < 0))
       st = st.strip()
       taken_first = False
       final_cmd = ""
       if(fake_cmd and (st.startswith("% phenix.") or
          st.startswith("% cctbx.") or
          st.startswith("% mmtbx.") or
          st.startswith("% elbow."))):
          amp_counter += 1
          cmd = st
          if(st.endswith(slash)):
             cmd = cmd.replace(slash, "")
             pick_next = True
             taken_first = True
          else:
             cmd = cmd.replace("% ","")
             separator = "\n"+"-"*79+"\n"
             final_cmd = cmd
             cmd_counter += 1
             pick_next = False
             cmd = ""
       if(pick_next and not taken_first):
          print_line = False
          if(st.endswith(slash)):
             st = st.replace(slash, "")
             cmd = cmd + st
          else:
             print_line = True
             cmd = cmd + st
             pick_next = False
          if(print_line):
             cmd = cmd.replace("% ","")
             separator = "\n"+"."*79+"\n"
             final_cmd = cmd
             cmd_counter += 1
       if(final_cmd != ""):
          final_cmd = final_cmd.replace("data.hkl", hkl)
          final_cmd = final_cmd.replace("data_anom.hkl", hkl_anom)
          final_cmd = final_cmd.replace("model.pdb", pdb)
          final_cmd = final_cmd.replace("model_o5t.pdb", pdb_o5t)
          final_cmd = inject_parameter_file(final_cmd)
          if(final_cmd.count("phenix.refine")):
            if(final_cmd.count("main.number_of_macro_cycles=0")==0):
               final_cmd = final_cmd + " main.number_of_macro_cycles=2"
            final_cmd = final_cmd + " --overwrite" + " --quiet"

          if(final_cmd.count("phenix.pdbtools")):
            final_cmd = final_cmd + " --quiet"
          print separator
          print final_cmd
          if (not dry_run):
            os.environ["PHENIX_REGRESSION_DIR"]=libtbx.env.find_in_repositories(
                                             relative_path = "phenix_regression",
                                             test          = os.path.isdir)
            sys.stdout.flush()
            try: os.system(final_cmd)
            except KeyboardInterrupt: raise
            except:
              print "Cannot run the command:"
              print final_cmd
              print
              sys.stdout.flush()

  assert amp_counter == cmd_counter
  print "\nNumber of commands exercised: ", cmd_counter

if (__name__ == "__main__"):
  exercise(sys.argv[1:])
