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
Filler analyzer: Takes a TimeSeries object and returns a Float.

.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""
# standard library
import cmath
import numpy
import tvb.analyzers.metrics_base as metrics_base
import tvb.datatypes.time_series as time_series_module
from tvb.basic.filters.chain import FilterChain
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)



class KuramotoIndex(metrics_base.BaseTimeseriesMetricAlgorithm):
    """
    Return the Kuramoto synchronization index. 
    
    Useful metric for a parameter analysis when the collective brain dynamics
    represent coupled oscillatory processes.
    
    The *order* parameters are :math:`r` and :math:`Psi`.
    
    .. math::
		r e^{i * \\psi} = \\frac{1}{N}\\,\\sum_{k=1}^N(e^{i*\\theta_k})
    
    The first is the phase coherence of the population of oscillators (KSI) 
    and the second is the average phase.
    
    When :math:`r=0` means 0 coherence among oscillators.
    
    
    Input:
    TimeSeries datatype 
    
    Output: 
    Float
    
    This is a crude indicator of synchronization among nodes over the entire 
    network.

    #NOTE: For the time being it is meant to be another global metric.
    However, it should be consider to have a sort of TimeSeriesDatatype for this
    analyzer.
    
    """
    
    time_series = time_series_module.TimeSeries(
        label = "Time Series", 
        required = True,
        doc="""The TimeSeries for which the Kuramoto Synchronization Index
        will be computed""")
        
    
    accept_filter = FilterChain(operations = ["==", ">="], values = [4, 2],
                                fields=[FilterChain.datatype + '._nr_dimensions', FilterChain.datatype + '._length_2d'])
    
    
    def evaluate(self):
        """
        Kuramoto Synchronization Index
        """
        cls_attr_name = self.__class__.__name__+".time_series"
        self.time_series.trait["data"].log_debug(owner = cls_attr_name)
        
        
        if self.time_series.data.shape[1]  < 2:
            msg = " The number of state variables should be at least 2."
            LOG.error(msg)
            raise Exception, msg
                
        #TODO: Should be computed for each possible combination of var, mode
        #      for var, mode in itertools.product(range(self.time_series.data.shape[1]), 
        #                                         range(self.time_series.data.shape[3])):
        
        #TODO: Generalise. The Kuramoto order parameter is computed over sliding 
        #      time windows and then normalised    
        
        theta_sum = numpy.sum(numpy.exp(0.0 + 1j * (numpy.vectorize(cmath.polar)
                    (numpy.vectorize(complex)(self.time_series.data[:, 0, :, 0], 
                     self.time_series.data[:, 1, :, 0]))[1])), axis=1)
                     
        result = numpy.vectorize(cmath.polar)(theta_sum / self.time_series.data.shape[2])

        return result[0].mean()   
    
    
    def result_shape(self):
        """
        Returns the shape of the main result of the ... 
        """
        return (1,)
    
    
    def result_size(self):
        """
        Returns the storage size in Bytes of the results of the ... .
        """
        return 8.0 #Bytes
    
    
    def extended_result_size(self):
        """
        Returns the storage size in Bytes of the extended result of the ....
        That is, it includes storage of the evaluated ...
        """
        return 8.0 #Bytes


