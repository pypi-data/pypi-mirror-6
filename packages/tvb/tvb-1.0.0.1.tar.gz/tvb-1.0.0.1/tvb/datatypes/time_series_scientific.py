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
Scientific methods for the TimeSeries dataTypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import tvb.datatypes.time_series_data as time_series_data


class TimeSeriesScientific(time_series_data.TimeSeriesData):
    """ This class exists to add scientific methods to TimeSeriesData. """
    __tablename__ = None
    
    
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Time-series type": self.__class__.__name__}
        summary["Time-series name"] = self.title
        summary["Dimensions"] = self.labels_ordering
        summary["Time units"] = self.sample_period_unit
        summary["Sample period"] = self.sample_period
        summary["Length"] = self.sample_period * self.get_data_shape('data')[0]
        summary.update(self.get_info_about_array('data'))
        return summary



class TimeSeriesEEGScientific(time_series_data.TimeSeriesEEGData, 
                              TimeSeriesScientific):
    """ This class exists to add scientific methods to TimeSeriesEEGData. """
    pass
    
#    #NOTE: Explicitly adding number_of_sensors is sort of redundant given
#    #      "Shape" and "Dimensions", however, maybe worthwhile as convinience?
#    def _find_summary_info(self):
#        """ Extend the base class's summary dictionary. """
#        summary = super(TimeSeriesEEGScientific, self)._find_summary_info()
#        summary["Number of EEG sensors"] = self.sensors.number_of_sensors
#        return summary


class TimeSeriesMEGScientific(time_series_data.TimeSeriesMEGData, 
                              TimeSeriesScientific):
    """ This class exists to add scientific methods to TimeSeriesMEGData. """
    pass


class TimeSeriesSEEGScientific(time_series_data.TimeSeriesSEEGData, 
                              TimeSeriesScientific):
    """ This class exists to add scientific methods to TimeSeriesMEGData. """
    pass


class TimeSeriesRegionScientific(time_series_data.TimeSeriesRegionData, 
                                 TimeSeriesScientific):
    """
    This class exists to add scientific methods to TimeSeriesRegionData.
    """
    pass


class TimeSeriesSurfaceScientific(time_series_data.TimeSeriesSurfaceData, 
                                  TimeSeriesScientific):
    """
    This class exists to add scientific methods to TimeSeriesSurfaceData.
    """
    pass


class TimeSeriesVolumeScientific(time_series_data.TimeSeriesVolumeData,
                                 TimeSeriesScientific):
    """
    This class exists to add scientific methods to TimeSeriesVolumeData.
    """
    pass

