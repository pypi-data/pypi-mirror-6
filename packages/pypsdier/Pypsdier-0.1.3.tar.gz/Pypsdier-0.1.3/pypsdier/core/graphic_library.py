# -*- coding: utf-8 -*-
from matplotlib import pyplot
from matplotlib import rc

################################################################################
# COMMON DEFINITIONS
################################################################################
colors = ["b", "g", "r", "c", "m", "y", "k"]
lines  = ["-", "--", "-.", ":", "."]
ode_line = "--"
font = {'family' : 'Arial',
        'weight' : 'bold'}
rc('font', **font)
axes = {'grid':True}
rc('axes', **axes)
grid = {'color' : "k",
        'linestyle' : '-',
        'alpha' : 0.1,
        'linewidth' : 0.5}
rc('grid', **grid)

################################################################################
# AUXILIAR FUNCTIONS
################################################################################
def get_new_lims(lims, min=None, max=None, p=0.1):
  """
  Moves around the x/y lims a bit to avoid overlapping with axes
  """
  min = float(min) if min!=None else float(lims[0])
  max = float(max) if max!=None else float(lims[1])
  d = p*(max-min)
  return [min-d, max+d]

################################################################################
# PLOT THE RESULTS OF THE ODE SOLUTION
################################################################################
def plot_ode(T, C, legend="", xlabel="", ylabel="", title="", figname=""):
  """
  Plotting the ode solution stored on the solution dic
  """
  Ns, Nc = C.shape
  # PLOTING  
  fig = pyplot.figure()
  ax = pyplot.subplot(111)
  for i in range(Nc):
    c = C[:,i]
    ax.plot(T, c, colors[i]+ode_line, label=legend[i], lw=2.0)
  # Shink size to fit legend
  box = ax.get_position()
  ax.set_position([box.x0, box.y0 + box.height * 0.1,
                   box.width, box.height * 0.9])
  ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10), 
            fancybox=True, shadow=True, ncol=Nc)
  fig.suptitle("ODE solution (no catalyst particles considered)")
  ax.set_xlabel('Time [s]')
  ax.set_ylabel('Concentration [mM]')
  ax.set_xlim(get_new_lims(ax.get_xlim()))
  ax.set_ylim(get_new_lims(ax.get_ylim(), min=0))
  if figname:
    pyplot.savefig(figname)
    pyplot.close()
  else:
    pyplot.show()
  return

################################################################################
# PLOT THE RESULTS OF THE PDE SOLUTION
################################################################################
def plot_pde(T, C, legend, xlabel="", ylabel="", title="", figname=""):
  """
  Plotting the pde solution.
  Only bulk concentrations (all radiuses have the same value)
  """
  # Get the numbers
  Nr = len(C)
  Nc = len(C[0])
  # PLOTING  
  fig = pyplot.figure()
  ax = pyplot.subplot(111)
  for i in range(Nc):
    c = C[0][i][:,-1]
    ax.plot(T, c, colors[i], label=legend[i], lw=2.0)
  # Shink size to fit legend
  box = ax.get_position()
  ax.set_position([box.x0, box.y0 + box.height * 0.1,
                   box.width, box.height * 0.9])
  ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10), 
            fancybox=True, shadow=True, ncol=Nc)
  fig.suptitle("PDE solution")
  ax.set_xlabel('Time [s]')
  ax.set_ylabel('Concentration [mM]')
  ax.set_xlim(get_new_lims(ax.get_xlim()))
  ax.set_ylim(get_new_lims(ax.get_ylim(), min=0))
  if figname:
    pyplot.savefig(figname)
    pyplot.close()
  else:
    pyplot.show()
  return

################################################################################
# COMPARE ODE AND PDE RESULTS
################################################################################
def plot_ode_and_pde(T_ode, C_ode, T_pde, C_pde, legend="", xlabel="", ylabel="", title="", figname=""):
  """
  Plotting the ode solution stored on the solution dic
  """
  # Get the numbers
  Nr = len(C_pde)
  Nc = len(C_pde[0])
  # Get the max
  Cmax = 0
  for j in range(Nr):
    for i in range(Nc):
      Cmax = max(Cmax, C_pde[j][i][:,-1].max())
  # Plotting
  fig = pyplot.figure()
  # Get nice subplots
  ax = []
  for i in range(Nc):
    if Nc==1:
      ax.append(pyplot.subplot(1,1,i+1))
    elif Nc==3:
      ax.append(pyplot.subplot(3,1,i+1))
    else:
      ax.append(pyplot.subplot((Nc+1)/2,2,i+1))
  # Plotting
  for i in range(Nc):
    c = C_ode[:,i]
    ax[i].plot(T_ode, c, colors[i]+ode_line, label="ODE ", lw=2.0, alpha=0.5)
    c = C_pde[0][i][:,-1]
    ax[i].plot(T_pde, c, colors[i]+lines[0], label="PDE", lw=2.0)

  for i in range(len(ax)):
    ax[i].set_xlabel('Time [s]')
    ax[i].set_ylabel('Concentration [mM]')
    ax[i].set_xlim(get_new_lims(ax[i].get_xlim()))
    ax[i].set_ylim(get_new_lims(ax[i].get_ylim(), min=0, max=Cmax))
    ax[i].set_title(legend[i], horizontalalignment="right", x=1.0)

  fig.suptitle("Concentrations for the ODE (dashed lines) and PDE (continuous line)")
  fig.subplots_adjust(wspace=0.3, hspace = 0.4)
  if figname:
    pyplot.savefig(figname)
    pyplot.close()
  else:
    pyplot.show()
  return
