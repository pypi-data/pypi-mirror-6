# -*- coding: utf-8 -*-
from xlwt import Workbook, easyxf
import numpy as np
from pdb import set_trace as st

##########################################################################
# Fonts
##########################################################################
title = easyxf('font: bold on; align: wrap on;')
subtitle = easyxf('font: italic on; align: wrap on;')

##########################################################################
# Wrappers and helpers
##########################################################################
def write_to_xls(ws, i_ws, j_ws, A, font=''):
  """
  Wrapper to write a matrix into a workbook into a specific position
  """
  if type(A)==str:
    if font:
      ws.write(i_ws, j_ws, A, font)
    else:
      ws.write(i_ws, j_ws, A)
  else:
    A = np.matrix(A)
    n, m = A.shape
    for i in xrange(n):
      for j in xrange(m):
        if font:
          ws.write(i_ws+i,j_ws+j,A[i,j],font)
        else:
          ws.write(i_ws+i,j_ws+j,A[i,j])
  return

def xls_header(ws,n,m=-1):
  """
  ??x  
  """
  ws.set_panes_frozen(True)
  ws.set_horz_split_pos(n)
  if m>0:
    ws.set_vert_split_pos(m)
  ws.set_remove_splits(True)
  return

##########################################################################
# Export the data-dictionary as a spreadsheet
##########################################################################
def save_as_spreadsheet(sol, filename):
  """
  export_to_xls allows to export the solution
  of the simulation in format xls 
  """
  wb = Workbook()
  write_parameters_sheet(wb, sol)
  if sol.has_key("ODE") and sol.has_key("PDE"):
    write_ode_and_pde_sheet(wb, sol)
  #if sol.has_key("ODE"):
  #  write_ode_xls(wb, sol)
  #if sol.has_key("PDE"):
  #  write_pde_xls(wb, sol)
  wb.save(filename)
  return

##########################################################################
# Writing the ode and pde times and concentrations on bulk module
##########################################################################
def write_ode_and_pde_sheet(wb, p):
  Nc = len(p["Names"])
  Nr = len(p["CatalystParticleRadius"])
  Np = len(p["ReactionParameters"])

  # Writing the parameters
  ws = wb.add_sheet("bulk ODE-PDE")

  # Writing the ODE
  n = 0
  write_to_xls(ws, 0, n, "ODE", title)
  t = p["ODE"]["t"]
  write_to_xls(ws, 1, n, "Time [s]", subtitle)
  write_to_xls(ws, 2, n, t.reshape(len(t),1))
  for i in range(Nc):
    c = p["ODE"]["C"][:,i]
    write_to_xls(ws, 1, n+1+i, p["Names"][i] + " [mM]", subtitle)
    write_to_xls(ws, 2, n+1+i, c.reshape(len(c),1))
   
  # Writing the PDE
  n = Nc+2
  write_to_xls(ws, 0, n, "PDE", title)
  t = p["PDE"]["t"]
  write_to_xls(ws, 1, n, "Time [s]", subtitle)
  write_to_xls(ws, 2, n, t.reshape(len(t),1))
  for i in range(Nc):
    c = p["PDE"]["C"][0][i][:,-1] # All radius have the same bulk concentration
    write_to_xls(ws, 1, n+1+i, p["Names"][i] + " [mM]", subtitle)
    write_to_xls(ws, 2, n+1+i, c.reshape(len(c),1))
  
  return
    
##########################################################################
# Saving the parameters into the xls
##########################################################################
def write_parameters_sheet(wb, p):
  Nc = len(p["Names"])
  Nr = len(p["CatalystParticleRadius"])
  Np = len(p["ReactionParameters"])

  # Writing the parameters
  ws1 = wb.add_sheet('Parameters')

  # Parameters    
  path_to_seed = p["Path"] + p["SeedFile"]
  write_to_xls(ws1, 0, 0, "File generated with pypsdier from seed %s" %path_to_seed, italic)

  # Catalyst
  n = 0
  write_to_xls(ws1, 2, n, "Catalyst", title)
  write_to_xls(ws1, 3, n, "Catalyst Volume")
  write_to_xls(ws1, 4, n, "Vc [ml]")
  write_to_xls(ws1, 4, n+1, p["CatalystVolume"])
  write_to_xls(ws1, 5, n, "Catalyst Enzyme Concentration")
  write_to_xls(ws1, 6, n, "E0 [mM]")
  if type(p["CatalystEnzymeConcentration"]) in [float, int]: 
    write_to_xls(ws1, 6, n+1, p["CatalystEnzymeConcentration"])
  else:
    write_to_xls(ws1, 6, n+1, "Given as function of time, see original file")
  write_to_xls(ws1, 7, n, "Thiele Modulus")
  write_to_xls(ws1, 8, n, "Phi")
  write_to_xls(ws1, 8, n+1, 0)  # FIX HERE
  write_to_xls(ws1, 9, n, "Radiuses values and frequencies")  # FIX HERE
  for i in range(Nr):
    R = p["CatalystParticleRadius"][i] / 1.E-6
    f = p["CatalystParticleRadiusFrequency"][i]
    write_to_xls(ws1, 10+i, n, "R [um]")
    write_to_xls(ws1, 10+i, n+1, R)
    write_to_xls(ws1, 10+i, n+2, " with probability ")
    write_to_xls(ws1, 10+i, n+3, f)

  # Reaction Conditions
  n = 5
  write_to_xls(ws1, 2, n, "Reaction Conditions", title)
  write_to_xls(ws1, 3, n, "Bulk Volume")
  write_to_xls(ws1, 4, n, "Vb [ml]")
  write_to_xls(ws1, 4, n+1, p["BulkVolume"])
  write_to_xls(ws1, 5, n, "Initial Concentrations")  
  for i in range(Nc):
    write_to_xls(ws1, 6+i, n, p["Names"][i] + " [mM]")
    write_to_xls(ws1, 6+i, n+1, p["InitialConcentrations"][i])

  # Reaction-Diffusion Parameters
  n = 8
  write_to_xls(ws1, 2, n, "Reaction-Diffusion Parameters", title)
  write_to_xls(ws1, 3, n, "Effective Diffusion Coefficient") 
  for i in range(Nc):
    write_to_xls(ws1, 4+i, n, p["Names"][i] + " [m2/s]")
    write_to_xls(ws1, 4+i, n+1, p["EffectiveDiffusionCoefficients"][i])
  write_to_xls(ws1, 4+Nc, n, "Reaction Function")
  write_to_xls(ws1, 5+Nc, n, "Name")
  write_to_xls(ws1, 5+Nc, n+1, p["ReactionFunction"]["Name"])
  write_to_xls(ws1, 6+Nc, n, "Reaction Parameters")
  for i in range(Np):
    # Ask for them with reverse notation to skip over first unnecessary values
    write_to_xls(ws1, 7+Nc+i, n, p["ReactionFunction"]["Arguments"][2+i])
    write_to_xls(ws1, 7+Nc+i, n+1, p["ReactionParameters"][i])

  # Simulation Parameters
  n = 11
  write_to_xls(ws1, 2, n, "Simulation Parameters", title)
  write_to_xls(ws1, 3, n, "Simulation Time")
  write_to_xls(ws1, 4, n, "Tsim [s]")
  write_to_xls(ws1, 4, n+1, p["SimulationTime"])
  write_to_xls(ws1, 5, n, "Saving Time Step dt [s]")
  write_to_xls(ws1, 6, n, "dt [s]")
  write_to_xls(ws1, 6, n+1, p["SavingTimeStep"])
  return

##########################################################################
# Converting the results of the ode in the dict to a xls
##########################################################################
def get_stylesheet_from_ode(sol):
    wb = Workbook()
    # Define fonts
    title = easyxf('font: bold on')
    subtitle = easyxf('font: bold on')

    # UNPACKING THE SOLUTION
    Txls = array([sol['T']]).T
    Cxls = sol['C']
    reaction_rate, params = sol['PR']
    IC, V, legend, Tsim = sol['PC']
    dt = sol['PS']
    # Create the workbook

    # SOME CALCULS  
    Nr, Nc = len(Cxls), len(Cxls[0])

    # Writing into the worksheet
    ws1 = wb.add_sheet('Parameters')    
    write_to_xls(ws1, 0, 0, "File generated with pypsdier", title)
    write_to_xls(ws1, 2, 0, "Catalyst")
    write_to_xls(ws1, 3, 0, "R (um)")
    write_to_xls(ws1, 3, 0, "Eo (mM)")
    write_to_xls(ws1, 3, 0, "Vc (ml)")
    write_to_xls(ws1, 3, 0, "Thiele modulus")
    
    return

##########################################################################
# Converting the results of the pde in the dict to a xls
##########################################################################
def get_stylesheet_from_pde(pde_params):
  """
  Exports the given solution as a xls stylesheet
  """

  wb = Workbook()
  title = easyxf('font: bold on')
  subtitle = easyxf('font: bold on')

  # Unpacking the values
  seed_file = pde_params["SeedFile"]
  Tsim = pde_params["SimulationTime"]
  dt_save = pde_params["SavingTimeStep"]
  Vc = pde_params["CatalystVolume"]
  Vb = pde_params["BulkVolume"]
  legend = pde_params["Names"]
  IC = pde_params["InitialConcentrations"]
  D = pde_params["EffectiveDiffusionCoefficients"]
  H_R = pde_params["CatalystParticleRadius"]
  H_f = pde_params["CatalystParticleRadiusFrequency"]
  reaction_rate = pde_params["ReactionFunction"]
  params = pde_params["ReactionParameters"]
  E = pde_params["CatalystEnzymeConcentration"]

  # UNPACKING THE SOLUTION
  Txls = array().T
  Cxls = sol['C']
  Nx, Nc, Nr, Nt, dt, dt_save = sol['PS']
  v_dx = array([arange(Nx+1.0)/Nx])

  # Parameter Worksheet
  ws1 = wb.add_sheet('Params')
    
  write_to_xls(ws1,0, 0, 'PARAMETERS OF THE SIMULATION',title)
  write_to_xls(ws1,1,0,'Nx')
  write_to_xls(ws1,1,1,Nx)
  write_to_xls(ws1,1,3,'Spatial Discretisation')
  write_to_xls(ws1,2,0,'dt')
  write_to_xls(ws1,2,1,dt)
  write_to_xls(ws1,2,3,'Temporal Discretisation')
  write_to_xls(ws1,3,0,'Tsim')
  write_to_xls(ws1,3,1,Txls[-1])
  write_to_xls(ws1,3,3,'Total Simulation Time')
    
  write_to_xls(ws1,5, 0, 'PARAMETERS OF THE PARTICLE SIZE DISTRIBUTION',title)
  write_to_xls(ws1,6,0,'H_r')
  write_to_xls(ws1,6,2+Nr,'Allowed radii [1E6 * m]')
  write_to_xls(ws1,6, 1, array(H_R)*1E6)
  write_to_xls(ws1,7,0,'H_f')
  write_to_xls(ws1,7, 1, H_f)
  write_to_xls(ws1,7,2+Nr,'Frequence (probability) of the radii')

  write_to_xls(ws1,9, 0, 'PARAMETERS OF THE REACTION',title)
  write_to_xls(ws1,11,2,legend)
  write_to_xls(ws1,12,0,'De')
  write_to_xls(ws1,12,Nc+2,'Effective Diffusion of Concentrations [E-10 m2/s]')
  write_to_xls(ws1,12, 1, array(D)*1E10)
  write_to_xls(ws1,13,0,'IC')
  write_to_xls(ws1,13, 1, array(IC))
  write_to_xls(ws1,13,Nc+2,'Initial Conditions for the Concentrations [mM]')
  write_to_xls(ws1,15,0,'Vc')
  write_to_xls(ws1,15,1,Vc)
  write_to_xls(ws1,15,3,'Total Catalyst Volume ')
  write_to_xls(ws1,16,0,'Vb')
  write_to_xls(ws1,16,1,Vb)
  write_to_xls(ws1,16,3,'Total (Liquid) Bulk Volume ')
  write_to_xls(ws1,18,0,'Kinetical parameters (depends on the def. of the function Reaction)')
  write_to_xls(ws1,19,0, array(params))
  write_to_xls(ws1,19,1+len(params),'Different units')
  write_to_xls(ws1,20,0,reaction_rate.__doc__)

  # Bulk Concentrations Worksheet
  ws2 = wb.add_sheet('Bulk')
  write_to_xls(ws2, 0, 0, 'Bulk concentrations [mM]')
  write_to_xls(ws2, 1, 0, 'T [s]')   # time title
  write_to_xls(ws2, 2, 0, Txls)      # time vector
  for ic in xrange(Nc):
      write_to_xls(ws2, 1, 1+ic,legend[ic])
      Cb = array([Cxls[0][ic][:,-1]]).T # Bulk concentration
      write_to_xls(ws2,2,1+ic, Cb)
  xls_header(ws2,2)
    
  if True:
      # Each Concentration Sheet
      wbc = []
      for ic in xrange(Nc):
        # Creando la pagina
        wbc.append(wb.add_sheet(legend[ic]))
        # Poniendo el tiempo
        write_to_xls(wbc[ic], 0, 0, 'T [s]')
        write_to_xls(wbc[ic], 3, 0, Txls) 
        for ir in xrange(Nr):
          write_to_xls(wbc[ic], 0, 3+ir*(Nx+2), 'C(r,t)')
          write_to_xls(wbc[ic], 0, 5+ir*(Nx+2), 'Rmax')
          write_to_xls(wbc[ic], 0, 6+ir*(Nx+2), 1E6*H_R[ir])
          write_to_xls(wbc[ic], 0, 7+ir*(Nx+2), '[1E-6 m]')
          write_to_xls(wbc[ic], 1, 2+ir*(Nx+2), v_dx)
          write_to_xls(wbc[ic], 3, 2+ir*(Nx+2), Cxls[ir][ic])
        xls_header(wbc[ic],2,1)
  return wb

