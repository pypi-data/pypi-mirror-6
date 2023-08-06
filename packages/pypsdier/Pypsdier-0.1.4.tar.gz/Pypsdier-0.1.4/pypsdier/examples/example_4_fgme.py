# -*- coding: utf-8 -*-
import pypsdier

################################################################################
# AUXILIAR DEFINITIONS OF REACTION AND ENZIMATIC CHARGE
################################################################################
def ReaccionCefalexina(Cs, E0, k1 ,k2, k3, k_3):
  """
  ReaccionCefalexina(Cs, E0, params)
  E0 [mM]
  params = k1 ,k2, k3, k_3 [mM]
  """
  ADCA, CEX, FG, FGME = Cs
  mcd = k1*FGME + k2 + k3*ADCA + k_3*CEX
  v_S = E0*k1*k3*FGME*ADCA / mcd
  v_H = E0*k2*k_3*CEX / mcd
  v_E = E0*k1*k2*FGME / mcd
  v = [ v_H - v_S, v_S - v_H, v_H + v_E, -v_S - v_E ]
  return v
E0 = 0.132
params = 56.5/60.,3407.4/60.,101.1/60.,14.3/60.  #[mM/s] 

################################################################################
# THE DICT params WILL CONTAIN ALL THE REQUIRED INFORMATION
# MUST PROVIDE A UNIQUE SEED FOR THE EXPERIMENT (WILL OVERWRITE FILE IF EXISTS)
# Names, InitialConditions, EffectiveDiffusionCoefficients MUST HAVE THE SAME NUMBER OF ELEMENTS
# Radiuses, RadiusesFrequencies MUST HAVE THE SAME NUMBER OF ELEMENTS
# ReactionParameters NEEDS TO BE COMPATIBLE WITH THE DEFINITION OF THE ReactionFunction
################################################################################
pde_params = {}
pde_params["SeedFile"] = "example_4_fgme.rde" # filename where the simulation will be stored
pde_params["SimulationTime"] = 5. # [s], total time to be simulated 
pde_params["SavingTimeStep"] = 1. # [s], saves only one data per second
pde_params["CatalystVolume"]  = 0.146 # [mL], total volume of all catalyst particles in reactor
pde_params["BulkVolume"]  = 25.0  # [mL], bulk volume of the liquid phase
pde_params["Names"] = ('ADCA', 'CEX', 'FG', 'FGME') # legend for the xls, reports and plots
pde_params["InitialConcentrations"] = (0., 0., 0., 10.92) # [mM], initial concentration of substrates and products
pde_params["EffectiveDiffusionCoefficients"] = (5.71E-10, 5.09E-10, 5.68E-10, 5.65E-10)  # [m2/s], effective diffusion coefficient for substrates and products
pde_params["CatalystParticleRadius"] = (75.7E-6,) # [m], list of possible catalyst particle radiuses
pde_params["CatalystParticleRadiusFrequency"] = (1.0,) # [], list of corresponding frequencies of catalyst particle radiuses
pde_params["ReactionFunction"] = ReaccionCefalexina # function defining the reaction 
pde_params["ReactionParameters"] = params   # [mM/s], parameters to be used in the reaction function 
pde_params["CatalystEnzymeConcentration"] = E0 # [mM] can be a float, int or a function returning float or int. 

################################################################################
# SOLVE THE PDE AND SAVE THE RESULT INTO THE SEED
################################################################################
pypsdier.pde(pde_params)
pypsdier.ode(pde_params)
