from cStringIO import StringIO
import mmtbx.command_line.maps

def run():
  log = StringIO()
  mmtbx.command_line.maps.run(args=["NO_PARAMETER_FILE"], log = log)
  ofn = open("phenix_maps.txt","w")
  ofn.write(log.getvalue())
  ofn.close()

if (__name__ == "__main__"):
  run()
