# -*- coding: utf-8 -*-
from scipy.integrate import odeint
import numpy as np
import sys
import seed_library as seed

from pdb import set_trace as st

################################################################################
# MAIN SOLVER OF THE ODE
################################################################################
def ode(ode_params, master_file=sys.argv[0]):
  """
  Wrapper for using scipy ode solver with our notation 
  """
  # Add the masterfile
  ode_params["MasterFile"] = master_file

  # Unpacking the values
  Reaction = ode_params["ReactionFunction"]
  params = ode_params["ReactionParameters"]
  Tsim = ode_params["SimulationTime"]
  Vc = ode_params["CatalystVolume"]
  Vb = ode_params["BulkVolume"]
  legend = ode_params["Names"]
  IC = ode_params["InitialConcentrations"]
  D = ode_params["EffectiveDiffusionCoefficients"]
  E0 = ode_params["CatalystEnzymeConcentration"]

  # Path where simulation will be saved
  path_to_seed = "/".join(master_file.split("/")[:-1] + [ode_params["SeedFile"]])

  # DEFINING A LOCAL REACTION
  # E0 must be corrected for incluying dilution
  dilusion = (Vc+Vb)/Vb

  def diluted_E(t, dilution):
    if type(E0)==float or type(E0)==int:
      return dilusion*E0
    else:
      return dilusion*E0(t)

  def ode_reaction(C, ti, diluted_E, dilusion, local_params):
    E_t = diluted_E(ti, dilusion)
    return Reaction(C, E_t, *params)

  # DEFINING THE TIME TO SIMULATE
  dt = 0.01
  if ode_params.has_key("PDE"):
    T = ode_params["PDE"]["t"]
  else:
    T = np.arange(0.0, Tsim+dt, dt) 

  # ODE SOLUTION 
  C = odeint(ode_reaction, IC, T, args=(diluted_E, dilusion, params))

  # Adding the new information to the dict
  ode_params["ODE"] = {"t":T, 
                               "C":C, 
                               "dt":dt, 
                               "method":"scipy.odeint"}

  # Save the dic
  seed.plant(ode_params, path_to_seed)
  return
