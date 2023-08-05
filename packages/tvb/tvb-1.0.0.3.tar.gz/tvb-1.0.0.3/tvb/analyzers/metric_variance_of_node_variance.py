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

.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""
#TODO: Currently built around the Simulator's 4D timeseries -- generalise...
import tvb.analyzers.metrics_base as metrics_base
import tvb.datatypes.time_series as time_series_module
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)



class VarianceNodeVariance(metrics_base.BaseTimeseriesMetricAlgorithm):
    """
    Zero-centres all the time-series, calculates the variance for each node 
    time-series and returns the variance of the node variances. 

    Input:
    TimeSeries datatype 
    
    Output: 
    Float
    
    This is a crude indicator of how different the "excitability" of the model is
    from node to node.
    """
    time_series = time_series_module.TimeSeries(
        label = "Time Series",
        required = True,
        doc="""The TimeSeries for which the variance of the zero centered node
            variance is to be computed.""")
    
    def evaluate(self):
        """
        Compute the zero centered variance of node variances for the time_series.
        """
        cls_attr_name = self.__class__.__name__+".time_series"
        self.time_series.trait["data"].log_debug(owner = cls_attr_name)
        
        shape = self.time_series.data.shape
        
        zero_mean_data = (self.time_series.data - self.time_series.data.mean(axis=0))
        #reshape by concat the time-series of each var and modes for each node.
        zero_mean_data = zero_mean_data.transpose((0, 1, 3, 2))
        cat_tpts = shape[0] * shape[1] * shape[3]
        zero_mean_data = zero_mean_data.reshape((cat_tpts, shape[2]), order="F")
        #Variance over time-points, state-variables, and modes for each node.
        node_variance = zero_mean_data.var(axis=0)
        #Variance of that variance over nodes
        result = node_variance.var()
        return result
    
    
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


