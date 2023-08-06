# -*- coding: utf-8 -*-
import pickle
import sys
import xls_library as xls
import graphic_library as gl
from pdb import set_trace as st

################################################################################
# Short function to print the original file
################################################################################
def print_file(seed_file):
  params = grow(seed_file)
  print "File used to generate the data:"
  print "-"*80
  print params["SimulationFile"]
  print "-"*80
  return

################################################################################
# Caller to the graphic_library to plot the results
################################################################################
def plot(seed_file):
  """
  Converts the seed_file into a xls file that can be open as a spreadsheet
  """
  sol = grow(seed_file)

  # ODE plot
  if sol.has_key("ODE"):
    figname = sol["Path"] + sol["SeedFile"].replace(".rde","_ode.png")
    gl.plot_ode(sol["ODE"]["t"], sol["ODE"]["C"],  
                legend=sol["Names"],
                figname=figname)

  # PDE plot
  if sol.has_key("PDE"):
    figname = sol["Path"] + sol["SeedFile"].replace(".rde","_pde.png")
    gl.plot_pde(sol["PDE"]["t"], sol["PDE"]["C"], 
                legend=sol["Names"],
                figname=figname)

  # ODE and PDE plot
  if sol.has_key("PDE") and sol.has_key("ODE"):
    figname = sol["Path"] + sol["SeedFile"].replace(".rde","_vs.png")
    gl.plot_ode_and_pde(sol["ODE"]["t"], sol["ODE"]["C"],
                        sol["PDE"]["t"], sol["PDE"]["C"],
                        legend = sol["Names"],
                        figname=figname)

  return
  
################################################################################
# Caller to the xls_library to convert the file
################################################################################
def convert_to_xls(seed_file):
  """
  Converts the seed_file into a xls file that can be open as a spreadsheet
  """
  sol = grow(seed_file)
  xls_file = seed_file.replace(".rde", ".xls")
  xls.save_as_spreadsheet(sol, xls_file)
  return
  
################################################################################
# Functions plant and grow wrap the pickle library and read/save a seed
################################################################################
def plant(dic, filename):
  """
  We deep copy the dict and eliminate the functions to avoid having trouble
  when opening
  """
  safe_dic = dic.copy()
  for key in safe_dic.keys():
    # If it's a function, can't save it, save only the function's name
    if type(safe_dic[key])==type(lambda x:x):
      safe_dic[key] = {"Name":safe_dic[key].__name__,
                       "Arguments":safe_dic[key].func_code.co_varnames}

  # Save the path
  safe_dic["Path"] = "/".join(safe_dic["MasterFile"].split("/")[:-1])+"/"

  # Add the lines from the master file
  with open(safe_dic["MasterFile"], "r") as mf:
    safe_dic["SimulationFile"] = "".join(mf.readlines())

  # Now save the dic
  with open(filename, "wb") as f:
    pickle.dump(safe_dic, f)
  return

def grow(filename):
  """
  Opens a file and returns whatever is inside.
  """
  with open(filename, "rb") as f:
    what = pickle.load(f)
  return what

################################################################################
# SMALL TESTING FOR DEBUG PURPOSES ON DIRECT EXECUTION
################################################################################
if __name__=="__main__":
  import os
  from pdb import set_trace as st

  print "*"*80 + "\nDebug routine\n" + "*"*80

  def myfun(x,y,z=0):
    """
    Multiline comment to break it all
    """
    return x*y+z

  d = {"int":1, 
       "float":3.14, 
       "list":[1,1,2,3,5,8,11],
       "tuple":(2,4,6,8,10),
       "function": myfun,
       "list_of_params": (myfun, 0, 1)
       }

  print "Saving d=%s into file \n" %str(d)
  filename = "test.pdr"
  plant(d, filename)
  del d
  #del myfun : If I delete myfun it will stop working!
  d2 = grow(filename)
  print "Reading d=%s from file \n" %str(d2)
  f = d2["function"]
  print "%f al cuadrado es %f" %(1.2, f(1.2,1.2))
  f2, a, b = d2["list_of_params"]
  print "%f al cuadrado es %f" %(2.0, f(2.0,2.0))  
  os.remove(filename)
