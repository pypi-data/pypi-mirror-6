# -*- coding: utf-8 -*-
import pypsdier
from math import exp

################################################################################
# AUXILIAR DEFINITIONS OF REACTION AND ENZIMATIC CHARGE
################################################################################
def MichaelisMenten(Cs, E0, k, K):
  """
  Definition for Michaelis Menten reaction with params k [1/s] and K [mM]
  """
  S, = Cs
  v_S = k*E0*S/(K+S)
  v = (-v_S,)
  return v

def CatalystEnzymeConcentration(t):
  """
  Enzyme Concentration in the catalyst particles, can vary in time due to several effects. 
  """
  E0 = 0.10 # [mM], initial concentration
  return E0*exp(-.1*t) # [mM]

################################################################################
# THE DICT params WILL CONTAIN ALL THE REQUIRED INFORMATION
# MUST PROVIDE A UNIQUE SEED FOR THE EXPERIMENT (WILL OVERWRITE FILE IF EXISTS)
# Names, InitialConditions, EffectiveDiffusionCoefficients MUST HAVE THE SAME NUMBER OF ELEMENTS
# Radiuses, RadiusesFrequencies MUST HAVE THE SAME NUMBER OF ELEMENTS
# ReactionParameters NEEDS TO BE COMPATIBLE WITH THE DEFINITION OF THE ReactionFunction
################################################################################
params = {}
params["SeedFile"] = "example_1_mm.rde" # filename where the simulation will be stored
params["SimulationTime"] = 5. # [s], total time to be simulated 
params["SavingTimeStep"] = 1. # [s], saves only one data per second
params["CatalystVolume"]  = 0.01 # [mL], total volume of all catalyst particles in reactor
params["BulkVolume"]  = 40.0  # [mL], bulk volume of the liquid phase
params["Names"] = ('PenG',)  # legend for the xls, reports and plots
params["InitialConcentrations"] = (1.3,)   # [mM], initial concentration of substrates and products
params["EffectiveDiffusionCoefficients"] = (5.30E-10,)  # [m2/s], effective diffusion coefficient for substrates and products
params["CatalystParticleRadius"] = [25.E-6, 50.E-6] # [m], list of possible catalyst particle radiuses
params["CatalystParticleRadiusFrequency"] = [0.5, 0.5] # [], list of corresponding frequencies of catalyst particle radiuses
params["ReactionFunction"] = MichaelisMenten # function defining the reaction 
params["ReactionParameters"] = (41 , 0.13)   # [1/s], [mM/s], parameters to be used in the reaction function after Cs and E0 
params["CatalystEnzymeConcentration"] = 0.001 #CatalystEnzymeConcentration # [mM] can be a float, int or a function returning float or int. 

################################################################################
# SOLVE THE PDE AND SAVE THE RESULT INTO THE SEED
################################################################################
pypsdier.pde(params)
pypsdier.ode(params)
