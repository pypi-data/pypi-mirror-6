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
Framework methods for the Spectral datatypes.

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""

import tvb.datatypes.spectral_data as spectral_data


class FourierSpectrumFramework(spectral_data.FourierSpectrumData):
    """
    This class exists to add framework methods to FourierSpectrumData.
    """
    __tablename__ = None
    
    def configure(self):
        """After populating few fields, compute the rest of the fields"""
        # Do not call super, because that accesses data not-chunked
        self.nr_dimensions = len(self.read_data_shape())
        for i in range(self.nr_dimensions): 
            setattr(self, 'length_%dd' % (i + 1), int(self.read_data_shape()[i]))
    
    def read_data_shape(self):
        """
        Expose shape read on field 'data'
        """
        return self.get_data_shape('array_data')
    
    def read_data_slice(self, data_slice):
        """
        Expose chunked-data access.
        """
        return self.get_data('array_data', data_slice)
    
    def write_data_slice(self, partial_result):
        """
        Append chunk.
        """
        #self.store_data_chunk('array_data', partial_result, grow_dimension=2, close_file=False)
        
        self.store_data_chunk('array_data', partial_result.array_data, grow_dimension=2, close_file=False)
        
        partial_result.compute_amplitude()
        self.store_data_chunk('amplitude', partial_result.amplitude, grow_dimension=2, close_file=False)
        
        partial_result.compute_phase()
        self.store_data_chunk('phase', partial_result.phase, grow_dimension=2, close_file=False)
        
        partial_result.compute_power()
        self.store_data_chunk('power', partial_result.power, grow_dimension=2, close_file=False)
        
        partial_result.compute_average_power()
        self.store_data_chunk('average_power', partial_result.average_power, grow_dimension=2, close_file=False)
        
        partial_result.compute_normalised_average_power()
        self.store_data_chunk('normalised_average_power', partial_result.normalised_average_power,
                              grow_dimension=2, close_file=False)



class WaveletCoefficientsFramework(spectral_data.WaveletCoefficientsData):
    """
    This class exists to add framework methods to WaveletCoefficientsData.
    """
    __tablename__ = None
    
    def configure(self):
        """After populating few fields, compute the rest of the fields"""
        # Do not call super, because that accesses data not-chunked
        self.nr_dimensions = len(self.read_data_shape())
        for i in range(self.nr_dimensions): 
            setattr(self, 'length_%dd' % (i + 1), int(self.read_data_shape()[i]))
    
    def read_data_shape(self):
        """
        Expose shape read on field 'data'
        """
        return self.get_data_shape('array_data')
    
    def read_data_slice(self, data_slice):
        """
        Expose chunked-data access.
        """
        return self.get_data('array_data', data_slice)
    
    def write_data_slice(self, partial_result):
        """
        Append chunk.
        """
        self.store_data_chunk('array_data', partial_result.array_data, grow_dimension=2, close_file=False)
        
        partial_result.compute_amplitude()
        self.store_data_chunk('amplitude', partial_result.amplitude, grow_dimension=2, close_file=False)
        
        partial_result.compute_phase()
        self.store_data_chunk('phase', partial_result.phase, grow_dimension=2, close_file=False)
        
        partial_result.compute_power()
        self.store_data_chunk('power', partial_result.power, grow_dimension=2, close_file=False)



class CoherenceSpectrumFramework(spectral_data.CoherenceSpectrumData):
    """
    This class exists to add framework methods to CoherenceSpectrumData.
    """
    __tablename__ = None
    
    def configure(self):
        """After populating few fields, compute the rest of the fields"""
        # Do not call super, because that accesses data not-chunked
        self.configure_chunk_safe()
    
    def read_data_shape(self):
        """
        Expose shape read on field 'data'
        """
        return self.get_data_shape('array_data')
    
    def read_data_slice(self, data_slice):
        """
        Expose chunked-data access.
        """
        return self.get_data('array_data', data_slice)
    
    def write_data_slice(self, partial_result):
        """
        Append chunk.
        """
        self.store_data_chunk('array_data', partial_result.array_data, grow_dimension=3, close_file=False)
                              

class ComplexCoherenceSpectrumFramework(spectral_data.ComplexCoherenceSpectrumData):
    """
    This class exists to add framework methods to ComplexCoherenceSpectrumData.
    """
    __tablename__ = None
    
    
    def configure(self):
        """After populating few fields, compute the rest of the fields"""
        # Do not call super, because that accesses data not-chunked

        self.configure_chunk_safe()
        
    def read_data_shape(self):
        """
        Expose shape read on field 'data'
        """
        return self.get_data_shape('array_data')
    
    def write_data_slice(self, partial_result):
        """
        Append chunk.
        """
        self.store_data_chunk('cross_spectrum', partial_result.cross_spectrum, grow_dimension=2, close_file=False)
                                
        self.store_data_chunk('array_data', partial_result.array_data, grow_dimension=2, close_file=False)
                               
        
