from libtbx import easy_run
import libtbx.load_env
import sys, os
from libtbx import smart_open

pdb = libtbx.env.find_in_repositories(
  relative_path="phenix_regression/pdb/phe_abc_w_h.pdb",
  test=os.path.isfile)

txt = libtbx.env.find_in_repositories(
  relative_path="phenix_html/rst_files/pdbtools.txt",
  test=os.path.isfile)

def exercise():
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
  # check selected commands
  example_1(commands)
  example_2(commands)
  example_3(commands)

def example_1(commands):
  selected_commands = [
    "% phenix.pdbtools model.pdb remove="+""""chain C or water" """,
    "% phenix.pdbtools model.pdb keep="+""""chain A or chain B" """,
    "% phenix.pdbtools model.pdb keep="+""""not(chain C or water)" """,
    "% phenix.pdbtools model.pdb remove="+""""not(chain A or chain B)" """]
  selected_commands_=[]
  for cmd in selected_commands:
    selected_commands_.append(cmd.strip())
  selected_commands = selected_commands_
  counter = 0
  for cmd in commands:
    if(cmd in selected_commands):
      counter += 1
      cmd = cmd.replace("model.pdb", pdb)
      cmd = cmd.replace("%", "")
      cmd += " output.pdb.file_name=check_equivalent_%s "%str(counter)
      easy_run.call(command = cmd)
  assert counter == 4
  f1=smart_open.for_reading(file_name="check_equivalent_1").read().splitlines()
  f2=smart_open.for_reading(file_name="check_equivalent_2").read().splitlines()
  f3=smart_open.for_reading(file_name="check_equivalent_3").read().splitlines()
  f4=smart_open.for_reading(file_name="check_equivalent_4").read().splitlines()
  for l1,l2,l3,l4 in zip(f1,f2,f3,f4):
    assert l1 == l2
    assert l3 == l4
    assert l1 == l4

def example_2(commands):
  selected_command = \
    "% phenix.pdbtools model.pdb keep=backbone set_b_iso=25"
  counter = 0
  for cmd in commands:
    if(cmd == selected_command):
      counter += 1
      cmd = cmd.replace("model.pdb", pdb)
      cmd = cmd.replace("%", "")
      cmd += " output.pdb.file_name=example_2 "
      easy_run.call(command = cmd)
  assert counter == 1
  f1 = smart_open.for_reading(file_name="example_2").read()
  expected_result = \
"""CRYST1   12.000   11.000   13.000  80.00  70.00 100.00 P 1
SCALE1      0.083333  0.014694 -0.035164        0.00000
SCALE2      0.000000  0.092312 -0.024020        0.00000
SCALE3      0.000000  0.000000  0.084586        0.00000
ATOM      8  C   PHE A   1       5.864   7.650   5.747  1.00 25.00           C
ATOM      9  O   PHE A   1       6.144   7.469   4.562  1.00 25.00           O
ATOM     11  N   PHE A   1       4.546   5.572   5.714  1.00 25.00           N
ATOM     12  CA  PHE A   1       5.193   6.557   6.572  1.00 25.00           C
ATOM     28  C   PHE B   1      11.961   6.316   5.313  1.00 25.00           C
ATOM     29  O   PHE B   1      11.902   5.976   4.132  1.00 25.00           O
ATOM     31  N   PHE B   1       9.817   5.175   5.710  1.00 25.00           N
ATOM     32  CA  PHE B   1      11.002   5.735   6.347  1.00 25.00           C
ATOM     48  C   PHE C   1      11.652  11.587   6.579  1.00 25.00           C
ATOM     49  O   PHE C   1      11.662  11.223   5.404  1.00 25.00           O
ATOM     51  N   PHE C   1       9.463  10.498   6.860  1.00 25.00           N
ATOM     52  CA  PHE C   1      10.618  11.048   7.561  1.00 25.00           C
END
"""
  assert f1 == expected_result

def example_3(commands):
  selected_command = \
    "% phenix.pdbtools model.pdb keep=backbone set_b_iso=25 selection="+""""chain C" """
  counter = 0
  selected_command = selected_command.strip()
  for cmd in commands:
    print cmd
    if(cmd == selected_command):
      counter += 1
      cmd = cmd.replace("model.pdb", pdb)
      cmd = cmd.replace("%", "")
      cmd += " output.pdb.file_name=example_3 "
      easy_run.call(command = cmd)
  assert counter == 1
  f1 = smart_open.for_reading(file_name="example_3").read()
  expected_result = \
"""CRYST1   12.000   11.000   13.000  80.00  70.00 100.00 P 1
SCALE1      0.083333  0.014694 -0.035164        0.00000
SCALE2      0.000000  0.092312 -0.024020        0.00000
SCALE3      0.000000  0.000000  0.084586        0.00000
ATOM      8  C   PHE A   1       5.864   7.650   5.747  1.00 17.21           C
ATOM      9  O   PHE A   1       6.144   7.469   4.562  1.00 17.39           O
ATOM     11  N   PHE A   1       4.546   5.572   5.714  1.00 17.13           N
ATOM     12  CA  PHE A   1       5.193   6.557   6.572  1.00 17.18           C
ATOM     28  C   PHE B   1      11.961   6.316   5.313  1.00 34.38           C
ATOM     29  O   PHE B   1      11.902   5.976   4.132  1.00 34.72           O
ATOM     31  N   PHE B   1       9.817   5.175   5.710  1.00 34.25           N
ATOM     32  CA  PHE B   1      11.002   5.735   6.347  1.00 34.35           C
ATOM     48  C   PHE C   1      11.652  11.587   6.579  1.00 25.00           C
ATOM     49  O   PHE C   1      11.662  11.223   5.404  1.00 25.00           O
ATOM     51  N   PHE C   1       9.463  10.498   6.860  1.00 25.00           N
ATOM     52  CA  PHE C   1      10.618  11.048   7.561  1.00 25.00           C
END
"""
  assert f1 == expected_result


if (__name__ == "__main__"):
  exercise()
