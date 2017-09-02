from libtbx.test_utils import show_diff
from libtbx import easy_run
from libtbx import smart_open
import libtbx.load_env
import time
import os

pdb = libtbx.env.find_in_repositories(
  relative_path="phenix_regression/pdb/phe_abc_w_h.pdb",
  test=os.path.isfile)

txt = libtbx.env.find_in_repositories(
  relative_path="phenix_html/rst_files/reference/pdbtools.txt",
  test=os.path.isfile)

def exercise():
  time0 = time.time()
  # extract commands and check their number
  assert [pdb, txt].count(None) == 0
  line_start = False
  slash = str("%s"%"\ ").strip()
  pick_next = False
  amp_counter = 0
  cmd_counter = 0
  commands = []
  for st in open(txt, "r").read().splitlines():
    st = st.strip()
    if(st.startswith("%")): amp_counter += 1
    taken_first = False
    final_cmd = ""
    if(st.startswith("% phenix.")):
      cmd_counter += 1
      cmd = st
      if(cmd.endswith(slash)):
        cmd = cmd.replace(slash, "")
        pick_next = True
      else:
        commands.append(cmd)
        pick_next = False
        cmd = ""
    if(pick_next and not st.startswith("% phenix.") and len(cmd) > 0):
      if(st.endswith(slash)):
        st = st.replace(slash, "")
        cmd = cmd + st
      else:
        cmd = cmd + st
        pick_next = False
        commands.append(cmd)
        cmd = ""
  assert amp_counter == cmd_counter
  print "Commands found:"
  for cmd in commands:
    print
    print cmd
  # exercise extracted commands (make sure they all run, do not check output)
  for cmd in commands:
    print
    cmd = cmd.replace("model.pdb", pdb)
    cmd = cmd.replace("%", "")
    print cmd
    easy_run.call(command = cmd)
  print "OK time %.2f" % (time.time() - time0)

if (__name__ == "__main__"):
  exercise()
