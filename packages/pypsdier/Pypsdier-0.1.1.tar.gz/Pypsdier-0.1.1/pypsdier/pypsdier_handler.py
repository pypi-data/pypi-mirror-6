#!/usr/bin/env python
"""@package docstring
 pypsdie: pythonistic reaction diffusion equations
 Date   : Jan, 2010.
 Author : Sebastian Flores
"""

################################################################################
# Libraries used directly from each file to create the seeds
################################################################################
from core.ode_library import ode
from core.pde_library import pde
from core.seed_library import grow, plant

################################################################################ 
#Decorator : check for inexisting files
################################################################################
def check_IOerror(func):
  """
  Decorator that easyly checks for inexisting files.
  """
  # Define the new function
  def checked_function(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except IOError:
      print "\nFile not found: %s\n" %args[0]
  # Return the new function
  return checked_function

################################################################################
# Decorator : check for valid extension
################################################################################
def check_valid_extension(func):
  """
  Decorator that checks if file has proper extension.
  """
  valid_extension = ".rde"
  # Define the new function
  def validated_extension(*args, **kwargs):
    filename = args[0]
    file_extension = filename[-4:]
    if (file_extension==valid_extension):
      func(*args, **kwargs)
    else:
      print "\nERROR: Extension not accepted.\n"
  # Return the new function
  return validated_extension


################################################################################
# Delegation to main functions using decorators to check correct usage
################################################################################
@check_valid_extension
@check_IOerror
def run_xls(seed_file):
  seed.convert_to_xls(seed_file)
  return

@check_valid_extension
@check_IOerror
def run_plot(seed_file):
  seed.plot(seed_file)
  return

@check_valid_extension
@check_IOerror
def run_file(seed_file):
  seed.print_file(seed_file)
  return


################################################################################
# Main delegates the process to the libraries
################################################################################
def main(options):
  if options["xls"]:
    run_xls(options["xls"])
  elif options["plot"]:
    run_plot(options["plot"])
  elif options["file"]:
    run_file(options["file"])
  return


################################################################################
# This is the main usage, to be used to process the file
################################################################################
if __name__=="__main__":
  # Required libraries
  import argparse
  import library.seed_library as seed

  # Create the parser
  parser = argparse.ArgumentParser(prog="pypdie.py", description="pythonistic reaction diffusion equations")
  parser.add_argument("--xls", help="Converts the seed file to a xls file", type=str)
  parser.add_argument("--plot", help="Generates the plots for the seed file", type=str)
  parser.add_argument("--file", help="Prints out the original *.py file that generated the seed file", type=str)
  options = vars(parser.parse_args())
  actions = [options["xls"], options["file"], options["plot"]]
  if (sum(bool(a) for a in actions))==1:
    main(options)
  else:
    parser.print_help()
    print "Example xls:\n\t python pypsdier --xls seed_file.rde"
    print "Example plot:\n\t python pypsdier --plot seed_file.rde"
    print "Example file:\n\t python pypsdier --file seed_file.rde"
