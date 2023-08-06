# -*- coding: utf-8 -*-

from scipy import * # ARREGLAR AQUI

def data_analysis(sol,reaction=None):
  '''
  Yield and Productivity Analysis
  i_p : index of the interesting product
  i_lr : index of the limit reactant
  '''
  # Verification
  if not sol['type']=='pde':
    print 'Solution not suited for data analysis'
    return
  # UNPACKING
  T = sol['T']
  C_list = sol['C']
  f_reaction, E, params = sol['PR']
  if reaction:
    f_reaction = reaction
  De, H_R, H_f = sol['PD']
  legend, IC, Vc, Vb, Tsim = sol['PC']
  Nx, Nc, Nr, Nt, dt, dt_save = sol['PS']

  ###############-----------################################
  ### EFECTIVENESS FACTOR
  # CALCULO DE LA REACCION
  rr = []
  for ir in xrange(Nr):
    rr.append(f_reaction(C_list[ir],E,params))
  N = len(rr[0]) # if number of reactions to study is diff.
  # Separacion de probabilidades
  Hr, Hf = array(H_R), array([H_f])
  ER3 = sum(Hr**3*Hf)
  v_dr =  arange(Nx+1.0)/Nx
  eta_r = []
  for ir in xrange(Nr):
    eta_r.append([])
    for ic in xrange(N):
      foo = trapz(rr[ir][ic]*v_dr**2,x=v_dr)
      eta_r[ir].append( 3* foo / rr[ir][ic][:,-1] )
  eta_r = array(eta_r)
  eta = []
  for ic in xrange(N):
    eta.append(dot(Hf*Hr**3,eta_r[:,ic])[0]/ER3)
  '''
  ###############-----------################################
  ### YIELD
  Y = S[:,i_p,-1]/S[:,i_lr,-1]
  # Maximum Yield
  am_Y = argmax(Y)
  print 'Mayimum Yield = %.2E [] obtained at t = %.1F [s]' %(Y[am_Y],T[am_Y])
  ###############-----------################################
  ### YIELD
  # Volumetric Productivity
  P = S[1:,i_p,-1]/T[1:]
  # Maximum Productivity
  am_P = argmax(P)
  print 'Mayimum Productivity = %.2E [] obtained at t = %.1F [s]' %(P[am_P],T[am_P])
  '''
  # PACKING
  da_sol = {}
  da_sol['Y']  = ([],[])#(T,Y)
  da_sol['P']  = ([],[])#(T[1:], P)
  da_sol['EF'] = (T, eta, N)
  da_sol['PC'] = sol['PC']
  da_sol['PR'] = sol['PR']
  da_sol['PD'] = sol['PD']
  da_sol['PS'] = sol['PS']
  da_sol['type'] = 'da'
  return da_sol
