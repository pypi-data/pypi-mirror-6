# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and 
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
#
# This program is free software; you can redistribute it and/or modify it under 
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details. You should have received a copy of the GNU General 
# Public License along with this program; if not, you can download it here
# http://www.gnu.org/licenses/old-licenses/gpl-2.0
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
Demonstrate using the simulator for a surface simulation.

``Run time``: approximately 2 min (workstation circa 2010).

``Memory requirement``: ~ 1 GB

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

# Third party python libraries
import numpy

"""
from tvb.basic.logger.builder import get_logger
LOG = get_logger(__name__)

#Import from tvb.simulator modules:
import tvb.simulator.simulator as simulator
import tvb.simulator.models as models
import tvb.simulator.coupling as coupling
import tvb.simulator.integrators as integrators
import tvb.simulator.monitors as monitors

import tvb.datatypes.connectivity as connectivity
import tvb.datatypes.surfaces as surfaces
import tvb.datatypes.equations as equations
import tvb.datatypes.patterns as patterns

from matplotlib.pyplot import *
from tvb.simulator.plot.tools import *
"""

from tvb.simulator.lab import *

##----------------------------------------------------------------------------##
##-                      Perform the simulation                              -##
##----------------------------------------------------------------------------##

LOG.info("Configuring...")
#Initialise a Model, Coupling, and Connectivity.
oscilator = models.Generic2dOscillator()
white_matter = connectivity.Connectivity()
white_matter.speed = numpy.array([4.0])

white_matter_coupling = coupling.Linear(a=2**-7)

#Initialise an Integrator
heunint = integrators.HeunDeterministic(dt=2**-4)

#Initialise some Monitors with period in physical time
mon_tavg = monitors.TemporalAverage(period=2**-2)
mon_savg = monitors.SpatialAverage(period=2**-2)
mon_eeg = monitors.EEG(period=2**-2)

#Bundle them
what_to_watch = (mon_tavg, mon_savg, mon_eeg)

#Initialise a surface
local_coupling_strength = numpy.array([2**-6])
default_cortex = surfaces.Cortex(coupling_strength = local_coupling_strength)

##NOTE: THIS IS AN EXAMPLE OF DESCRIBING A SURFACE STIMULUS AT REGIONS LEVEL. 
#       SURFACES ALSO SUPPORT STIMULUS SPECIFICATION BY A SPATIAL FUNCTION 
#       CENTRED AT A VERTEX (OR VERTICES).
#Define the stimulus
#Specify a weighting for regions to receive stimuli...
white_matter.configure() # Because we want access to number_of_regions
nodes = [0, 7, 13, 33, 42]
#NOTE: here, we specify space at region level simulator will map to surface 
#Specify a weighting for regions to receive stimuli... 
weighting = numpy.zeros((white_matter.number_of_regions, 1))
weighting[nodes] = numpy.array([2.0**-2, 2.0**-3, 2.0**-4, 2.0**-5, 2.0**-6])[:, numpy.newaxis]

eqn_t = equations.Gaussian()
eqn_t.parameters["midpoint"] = 8.0

stimulus = patterns.StimuliRegion(temporal = eqn_t,
                                  connectivity = white_matter, 
                                  weight = weighting)

#Initialise Simulator -- Model, Connectivity, Integrator, Monitors, and surface.
sim = simulator.Simulator(model = oscilator,
                          connectivity = white_matter,
                          coupling = white_matter_coupling,
                          integrator = heunint,
                          monitors = what_to_watch,
                          surface = default_cortex, stimulus = stimulus)

sim.configure()

#Clear the initial transient, so that the effect of the stimulus is clearer.
#NOTE: this is ignored, stimuli are defined relative to each simulation call.
LOG.info("Initial integration to clear transient...")
for _, _, _ in sim(simulation_length=128):
    pass

LOG.info("Starting simulation...")
#Perform the simulation
tavg_data = []
tavg_time = []
savg_data = []
savg_time = []
eeg_data = []
eeg_time = []
for tavg, savg, eeg in sim(simulation_length=2**5):
    if not tavg is None:
        tavg_time.append(tavg[0])
        tavg_data.append(tavg[1])

    if not savg is None:
        savg_time.append(savg[0])
        savg_data.append(savg[1])
        
    if not eeg is None:
        eeg_time.append(eeg[0])
        eeg_data.append(eeg[1])
    
LOG.info("finished simulation.")

##----------------------------------------------------------------------------##
##-               Plot pretty pictures of what we just did                   -##
##----------------------------------------------------------------------------##
    
#Plot the stimulus
plot_pattern(sim.stimulus)

if IMPORTED_MAYAVI:
    surface_pattern(sim.surface, sim.stimulus.spatial_pattern)

#Make the lists numpy.arrays for easier use.
TAVG = numpy.array(tavg_data)
SAVG = numpy.array(savg_data)
EEG = numpy.array(eeg_data)

#Plot region averaged time series
figure(3)
plot(savg_time, SAVG[:, 0, :, 0])
title("Region average")

#Plot EEG time series
figure(4)
plot(eeg_time, EEG[:, 0, :, 0])
title("EEG")

#Show them
show()

#Surface movie, requires mayavi.malb
if IMPORTED_MAYAVI:
    st = surface_timeseries(sim.surface, TAVG[:, 0, :, 0])

###EoF###