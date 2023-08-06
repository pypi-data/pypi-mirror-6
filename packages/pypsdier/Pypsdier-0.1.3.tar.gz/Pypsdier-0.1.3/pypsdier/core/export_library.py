from save_library import unpickle_from_file
from xls_library import save_as_stylesheet

from pdb import set_trace as st

def export_as_stylesheet(filename, report=""):
  sol = unpickle_from_file(filename)
  xls_filename = filename[:-4] + ".xls"
  save_as_stylesheet(sol, xls_filename, report)
  print "File %s has been exported as a stylesheet to %s" %(filename, xls_filename)
