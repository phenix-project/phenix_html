from __future__ import print_function
import sys

def run(args):
  def sort_it(inp):
    lines = inp.read().splitlines()
    lines.sort()
    for line in lines:
      print(line)
  if (len(args) == 0):
    sort_it(inp=sys.stdin)
  else:
    for file_name in args:
      sort_it(inp=open(file_name))

if (__name__ == "__main__"):
  run(sys.argv[1:])
