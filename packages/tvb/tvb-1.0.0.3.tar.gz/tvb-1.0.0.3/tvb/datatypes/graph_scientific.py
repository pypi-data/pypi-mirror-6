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

Scientific methods for the Graph datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import tvb.datatypes.graph_data as graph_data
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)



class CovarianceScientific(graph_data.CovarianceData):
    """ This class exists to add scientific methods to CovarianceData. """
    __tablename__ = None
    
    
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Graph type": self.__class__.__name__}
        summary["Source"] = self.source.title
        summary['Shape'] = self.get_data_shape('array_data')
        return summary


class ConnectivityMeasureScientific(graph_data.ConnectivityMeasureData):
    """
    Scientific methods for ConnectivityMeasure entity.
    """
    __tablename__ = None
    
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Graph type": self.__class__.__name__}
        #summary["Source"] = self.connectivity.title
        summary.update(self.get_info_about_array('array_data'))
        return summary
    
