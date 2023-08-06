# -*- coding: utf-8 -*-
import numpy as np
from scipy.linalg import solve
import sys
import seed_library as seed

################################################################################
# GENERATES THE MATRICES FOR THE ITERATION
################################################################################
def Matrices(H_R, H_f, Vc, Vb, Nx):
  H_R, H_f = np.array(H_R), np.array(H_f)/sum(H_f)
  nc = len(H_R)
  g = -3*Vc / (Vb*sum(H_f*H_R**3))
  Dr = np.array([-1.5, 2.,-0.5]) # One sided derivative from the right (LBC)
  Dl = np.array([ 0.5,-2., 1.5]) # One sided derivative from the left (RBC)
  dR = H_R/Nx # Delta R used for derivatives
  # Set up of matrices
  Id = np.eye(nc*Nx+1)
  Ls = np.zeros([nc*Nx+1,nc*Nx+1])
  bc = np.ones(nc*Nx+1)
  # auxiliary matrix
  i = range(0,Nx-1)
  vi = np.arange(1,Nx)
  C_aux = np.zeros([Nx-1,Nx+1])
  C_aux[range(0,Nx-1),range(0,Nx-1)] = 1. - 1./vi
  C_aux[range(0,Nx-1),range(1,Nx)] =  -2
  C_aux[range(0,Nx-1),range(2,Nx+1)] =  1. + 1./vi
  #jinv = 1./arange(1,Nx)
  #C_aux = diag(1-jinv,-1) -2*eye(Nx+1,Nx+1) + diag(1+jinv,1)
  # Fill up
  for c in range(nc):
    # LBC : imposed on the rows c*Nx
    Id[c*Nx,c*Nx] = 0
    Ls[c*Nx,c*Nx:(c*Nx+3)] = Dr/dR[c]
    bc[c*Nx] = 0
    # RBC : imposed on the last row
    Ls[-1,((c+1)*Nx-2):(c+1)*Nx] = g*H_f[c]*H_R[c]*Nx*Dl[0:-1]
    # RDE
    Ls[c*Nx+1:(c+1)*Nx,c*Nx:(c+1)*Nx] = C_aux[:,:-1]/dR[c]**2
    Ls[c*Nx+1:(c+1)*Nx,-1] = C_aux[:,-1]/dR[c]**2
  bc[-1] = 0   # LBC: avoid reaction 
  Ls[-1,-1] = g*sum(H_f*H_R)*Nx*Dl[-1] # RBC: gathered terms for Sb
  return Id, Ls, bc

################################################################################
# NO IDEA WHAT THIS WAS!!!
################################################################################
def nested_lists(C,Nx):
  Nt, Nc, N = C.shape
  Nr = (N-1)/Nx # Debe calzar justo justo
  C_list = []
  for ir in xrange(Nr):
    C_list.append([])
    for ic in xrange(Nc):
      C_intra = C[:,ic,ir*Nx:(ir+1)*Nx]
      C_bulk = np.array([C[:,ic,-1]]).T
      C_aux = np.concatenate( (C_intra,C_bulk), axis=1)
      C_list[ir].append( C_aux )
  return C_list


################################################################################
# AUXILIAR EVALUATION OF THE CATALYST ENZYME CONCENTRATION 'CAUSE CAN BE A FUNCTION
################################################################################
def eval_E(E, t):
  """
  Tries to evaluate the possibly function E, otherwise just returns the value E.
  """
  if type(E)==float or type(E)==int:
    return E
  else:
    try:
      return E(t)
    except:
      print "Something went awfully bad in eval_E(E,t)"
      return None
  return

def print_time(t, end_char=""):
  sys.stdout.write("\rTiempo Simulado PDE: %03d segundos %s" %(t,end_char))
  sys.stdout.flush()
  return

################################################################################
# MAIN SOLVER FOR THE PDE
################################################################################
def pde(pde_params, master_file=sys.argv[0], Nx=40, dt=-1):
  """
  Solver for the Reaction Diffusion Equation
  """
  # Add the masterfile
  pde_params["MasterFile"] = master_file

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
  Reaction = pde_params["ReactionFunction"]
  params = pde_params["ReactionParameters"]
  E = pde_params["CatalystEnzymeConcentration"]

  # Path where simulation will be saved
  path_to_seed = "/".join(master_file.split("/")[:-1] + [seed_file])

  # INDICES IMPORTANTES DE LA SIMULACION
  Nc = len(IC)       # Numero de concentraciones
  Nr = len(H_R) # Numero de radios distintos a considerar
  dt_max = (min(H_R)/Nx)**2 / max(D)
  if dt<0: #if not imposed by user
    dt = min(0.25*dt_max,0.1)

  ## CONSTRUCCION DE LAS MATRICES (fijas en las iteraciones)
  Mid, Mls, fic = Matrices(H_R, H_f, Vc, Vb, Nx)
  theta = 0.5
  ME, MI = [],[]
  for c in xrange(Nc):
    ME.append( np.matrix(Mid + dt*theta*D[c]*Mls) )
    MI.append( np.matrix(Mid - dt*(1-theta)*D[c]*Mls) )
  
  # INICIALIZACION DEL ALGORITMO
  ## INICIO DEL TIEMPO
  t = 0.0
  ## CONCENTRACIONES INICIALES
  v = np.zeros(Nr*Nx+1)
  v[-1]= 1
  C_old, C_new = [], []
  for c in xrange(Nc):
    C_old.append(v*IC[c])
  ## VELOCIDADES INICIALES
  v_C = Reaction(C_old, eval_E(E,t), *params)
  # GUARDAR VALORES INICIALES
  C_save, C_t = [], []
  for c in xrange(Nc):
    #C_save.append(float(C_old[c][-1]))
    C_save.append(C_old[c])
  C_t.append(C_save)
  T_t = [t,]
  # BUCLE CENTRAL
  if dt_save < 0:
    dt_save = 1.0 # incremental for saving simulation
  print_time(t)
  while t<Tsim:
    for c in xrange(Nc):
      b = ME[c]*np.matrix(C_old[c]).T + dt*np.matrix(v_C[c]*fic).T
      C_new.append( np.array(solve(MI[c],b).T)[0] )
    v_C = Reaction(C_new, eval_E(E,t), *params)
    C_old = C_new
    C_new = []
    t = t+dt
    if (t>T_t[-1]+dt_save):
      C_save = []
      for c in xrange(Nc):
        C_save.append(C_old[c])
      C_t.append(C_save)
      T_t.append(float(t))
      print_time(t)
  print_time(t, end_char="\n")
  Nt = len(T_t)

  # Adding the new information to the dict  
  pde_params["PDE"] = {"t":np.array(T_t), 
                       "dt":dt, 
                       "C":nested_lists(np.array(C_t), Nx)}

  # Save the dic
  seed.plant(pde_params, path_to_seed)
  return
