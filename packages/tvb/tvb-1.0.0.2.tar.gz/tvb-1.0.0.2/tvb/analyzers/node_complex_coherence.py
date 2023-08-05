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
Calculate the cross spectrum and complex coherence on a TimeSeries datatype and 
return a ComplexCoherence datatype.

.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""

import numpy
from scipy import signal as sp_signal
from tvb.datatypes.time_series import TimeSeries
import tvb.datatypes.spectral as spectral
import tvb.basic.traits.core as core
import tvb.basic.traits.types_basic as basic
import tvb.basic.traits.util as util
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)
SUPPORTED_WINDOWING_FUNCTIONS = ("hamming", "bartlett", "blackman", "hanning")


#NOTE: Work only with 2D TimeSeries -- otherwise a MemoryError will raise
        # My first attempts made use of itertools on the 4D TimeSeries but they were 
        # fruitless.
        # Nested `for` loops seem a 'good' solution instead of creating enormous ndarrays
        # to compute the FFT and derived complex spectra at once
#TODO: add more logs 

class NodeComplexCoherence(core.Type):
    """
    A class for calculating the FFT of a TimeSeries and returning
    a ComplexCoherenceSpectrum datatype.
   
  
    This algorithm is based on the matlab function data2cs_event.m written by Guido Nolte:
        .. [Freyer_2012] Freyer, F.; Reinacher, M.; Nolte, G.; Dinse, H. R. and
            Ritter, P. * Repetitive tactile stimulation changes resting-state
            functional connectivity-implications for treatment of sensorimotor decline.*
            Front Hum Neurosci, Bernstein Focus State Dependencies of Learning and
            Bernstein Center for Computational Neuroscience Berlin, Germany., 2012, 6, 144
    
    Input: 
    originally the input could be 2D (tpts x nodes/channels), and it was possible
    to give a 3D array (e.g., tpspt x nodes/cahnnels x trials) via the segment_length
    attribute. 
    Current TVB implementation can handle 4D or 2D TimeSeries datatypes. 
    Be warned: the 4D TimeSeries will be averaged and squeezed.
    
    Output: (main arrays)
    - the cross-spectrum
    - the complex coherence, from which the imaginary part can be extracted 
        
    By default the time series is segmented into 1 second `epoch` blocks and 0.5
    second 50% overlapping `segments` to which a Hanning function is applied. 
    
    """
    
    time_series = TimeSeries(
        label = "Time Series",
        required = True,
        doc = """The timeseries for which the CrossCoherence and ComplexCoherence
        is to be computed.""")
        
    epoch_length = basic.Float(
        label = "Epoch length [ms]",
        default = 1000.0,
        order = -1,
        required = False,
        doc = """In general for lengthy EEG recordings (~30 min), the timeseries 
        are divided into equally sized segments (~ 20-40s). These contain the 
        event that is to be characterized by means of the cross coherence. 
        Additionally each epoch block will be further divided into segments to 
        which the FFT will be applied.""")
    
    segment_length = basic.Float(
        label = "Segment length [ms]",
        default = 500.0,
        order = -1,
        required = False,
        doc = """The timeseries can be segmented into equally sized blocks
            (overlapping if necessary). The segement length determines the
            frequency resolution of the resulting power spectra -- longer
            windows produce finer frequency resolution. """)
            
    segment_shift = basic.Float(
        label = "Segment shift [ms]",
        default = 250.0,
        required = False,
        order = -1,
        doc = """Time length by which neighboring segments are shifted. e.g.
                `segment shift` = `segment_length` / 2 means 50% overlapping 
                segments.""")
    
    window_function = basic.String(
        label = "Windowing function",
        default = 'hanning',
        required = False,
        order = -1,
        doc = """Windowing functions can be applied before the FFT is performed.
             Default is `hanning`, possibilities are: 'hamming'; 'bartlett';
            'blackman'; and 'hanning'. See, numpy.<function_name>.""")
            
    average_segments = basic.Bool(
        label = "Average across segments",
        default = True,
        required = False,
        order = -1,
        doc = """Flag. If `True`, compute the mean Cross Spectrum across 
                segments.""")
        
    subtract_epoch_average = basic.Bool(
        label = "Subtract average across epochs",
        default = True,
        required = False,
        order = -1,
        doc = """Flag. If `True` and if the number of epochs is > 1, you can 
                optionally subtract the mean across epochs before computing the 
                complex coherence.""")
        
    zeropad = basic.Integer(
        label = "Zeropadding",
        default = 0,
        required = False,
        order = -1,
        doc = """Adds `n` zeros at the end of each segment and at the end 
        of window_function. It is not yet functional.""")
        
        
    detrend_ts = basic.Bool(
        label = "Detrend time series",
        default = False,
        required = False,
        order = -1,
        doc = """Flag. If `True` removes linear trend along the time dimension 
                before applying FFT.""")
        
    max_freq = basic.Float(
        label = "Maximum frequency",
        default = 1024.0,
        order = -1,
        required = False,
        doc = """Maximum frequency points (e.g. 32., 64., 128.) represented in 
                the output. Default is segment_length / 2 + 1.""")
        
    npat = basic.Float(
        label = "dummy variable",
        default = 1.0,
        required = False,
        order = -1,
        doc = """This attribute appears to be related to an input projection 
            matrix... Which is not yet implemented""")
        
    
    def evaluate(self):
        """
        Calculate the FFT, Cross Coherence and Complex Coherence of time_series 
        broken into (possibly) epochs and segments of length `epoch_length` and 
        `segment_length` respectively, filtered by `window_function`.
        """
        cls_attr_name = self.__class__.__name__+".time_series"
        self.time_series.trait["data"].log_debug(owner = cls_attr_name)
        tpts = self.time_series.data.shape[0]
        time_series_length = tpts * self.time_series.sample_period
        
        if len(self.time_series.data.shape) > 2:
            time_series_data = numpy.squeeze((self.time_series.data.mean(axis=-1)).mean(axis=1))
        
        #nchan = time_series_data.shape[1]
        
        #NOTE: if we get a projection matrix ... then ...
        #if self.npat > 1: 
        #    data = data * proj
        #    nchan = self.npat
        
        #Divide time-series into epochs, no overlapping
        if self.epoch_length > 0.0:
            nepochs = int(numpy.floor(time_series_length / self.epoch_length))
            epoch_tpts = self.epoch_length / self.time_series.sample_period
            time_series_length = self.epoch_length
            tpts = epoch_tpts
        else: 
            self.epoch_length = time_series_length
            nepochs = int(numpy.ceil(time_series_length / self.epoch_length))
            
        #Segment time-series, overlapping if necessary
        nseg = int(numpy.floor(time_series_length / self.segment_length))
        if nseg > 1:
            seg_tpts = self.segment_length / self.time_series.sample_period
            seg_shift_tpts = self.segment_shift / self.time_series.sample_period
            nseg = int(numpy.floor((tpts - seg_tpts) / seg_shift_tpts) + 1)
        else:
            self.segment_length = time_series_length
            seg_tpts = time_series_data.shape[0]

        # Frequency vectors
        freqs = numpy.fft.fftfreq(int(seg_tpts))
        nfreq = numpy.min([self.max_freq, numpy.floor((seg_tpts + self.zeropad) / 2.0) + 1])
        freqs = freqs[0:nfreq,] * (1.0/ self.time_series.sample_period)
        
        
        result_shape, av_result_shape = self.result_shape(
                                        self.time_series.data.shape, 
                                        self.max_freq, 
                                        self.epoch_length, 
                                        self.segment_length, 
                                        self.segment_shift, 
                                        self.time_series.sample_period, 
                                        self.zeropad, 
                                        self.average_segments)
        
        cs = numpy.zeros(result_shape, dtype=numpy.complex128)
        av = numpy.matrix(numpy.zeros(av_result_shape, dtype=numpy.complex128))
        coh = numpy.zeros(result_shape, dtype=numpy.complex128)

        # NOTE: result for individual epochs are kept only if npat > 1. Skipping ...
        #if self.npat > 1:
        #    if not self.average_segments:
        #        cs = numpy.zeros((nchan, nchan, nfreq, nepochs, nseg), dtype=numpy.complex128)
        #        av = numpy.zeros((nchan, nfreq, nepochs, nseg), dtype=numpy.complex128)
        #    else:
        #        av = numpy.zeros((nchan, nfreq, nepochs), dtype=numpy.complex128)
        #        cs = numpy.zeros((nchan, nchan, nfreq, nepochs), dtype=numpy.complex128) 
  


        #Apply windowing function
        if self.window_function is not None:
            if self.window_function not in SUPPORTED_WINDOWING_FUNCTIONS:
                LOG.error("Windowing function is: %s" % self.window_function)
                LOG.error("Must be in: %s" % str(SUPPORTED_WINDOWING_FUNCTIONS))
            
            window_function = eval("".join(("numpy.", self.window_function)))
            win = window_function(seg_tpts)
            window_mask = (numpy.kron(numpy.ones((time_series_data.shape[1], 1)), win)).T

        nave = 0
    
        for j in numpy.arange(nepochs):
            data = time_series_data[j*epoch_tpts:(j+1)*epoch_tpts, :]
        
            for i in numpy.arange(nseg): #average over all segments;
                time_series = data[i*seg_shift_tpts: i*seg_shift_tpts + seg_tpts, :]
            
                if self.detrend_ts:
                    time_series = sp_signal.detrend(time_series, axis=0)
            
                datalocfft = numpy.fft.fft(time_series * window_mask, axis=0)
                datalocfft = numpy.matrix(datalocfft)
            
                for f in numpy.arange(nfreq): #for all frequencies
                    if self.npat == 1:
                        if not self.average_segments:
                            cs[:, :, f, i] += numpy.conjugate(
                                              datalocfft[f, :].conj().T * \
                                              datalocfft[f, :])
                            av[:, f, i] += numpy.conjugate(datalocfft[f, :].conj().T)
                        else:
                            cs[:, :, f] += numpy.conjugate(
                                           datalocfft[f,:].conj().T * \
                                           datalocfft[f, :])
                            av[:, f] += numpy.conjugate(datalocfft[f, :].conj().T)
                    else:
                        if not self.average_segments:
                            cs[:, :, f, j, i] = numpy.conjugate(
                                                datalocfft[f, :].conj().T * \
                                                datalocfft[f, :])
                            av[:, f, j, i] = numpy.conjugate(datalocfft[f, :].conj().T)  
                        else:
                            cs[:, :, f, j] += numpy.conjugate(
                                           datalocfft[f,:].conj().T *\
                                           datalocfft[f,:])
                                                 
                            av[:, f, j] += numpy.conjugate(datalocfft[f, :].conj().T)  
                del datalocfft
          
            nave += 1.0
        
        # End of FORs
        if not self.average_segments:
            cs = cs / nave
            av = av / nave
        else:
            nave = nave * nseg
            cs = cs / nave
            av = av / nave
        
        # Subtract average
        for f in numpy.arange(nfreq):
            if self.subtract_epoch_average:
                if self.npat == 1:
                    if not self.average_segments:
                        for i in numpy.arange(nseg):
                            cs[:, :, f, i] = cs[:, :, f, i] - av[:, f, i] *  av[:, f, i].conj().T
                    else:
                        cs[:, :, f] = cs[:, :, f] - av[:, f] * av[:, f].conj().T
                else:
                    if not self.average_segments:
                        for i in numpy.arange(nseg):
                            for j in numpy.arange(nepochs):
                                cs[:, :, f, j, i] = cs[:, :, f, j, i] - av[:, f, j, i] * av[:, f, j, i].conj().T
                            
                    else: 
                        for j in numpy.arange(nepochs):
                            cs[:, :, f, j] = cs[:, :, f, j] - av[:, f, j] * av[:, f, j].conj().T
        
        #Compute Complex Coherence        
        ndim = len(cs.shape)
        if ndim == 3:
            for i in numpy.arange(cs.shape[2]):
                temp = numpy.matrix(cs[:, :, i])
                coh[:, :, i] = cs[:, :, i] / numpy.sqrt((temp.diagonal().conj().T) * temp.diagonal())
            
        elif ndim == 4:
            for i in numpy.arange(cs.shape[2]):
                for j in numpy.arange(cs.shape[3]):
                    temp = numpy.matrix(numpy.squeeze(cs[:, :, i, j]))
                    coh[:, :, i, j] = temp / numpy.sqrt((temp.diagonal().conj().T) * temp.diagonal().T)
        
        
        util.log_debug_array(LOG, cs, "result")
        spectra = spectral.ComplexCoherenceSpectrum(source = self.time_series,
                                  array_data = coh,
                                  cross_spectrum = cs,
    #                              frequency = freqs,
                                  epoch_length = self.epoch_length,
                                  segment_length = self.segment_length,
                                  windowing_function = self.window_function,
    #                             fft_points = seg_tpts,
                                  use_storage = False)
        return spectra
    
    
    @staticmethod
    def result_shape(input_shape, max_freq, epoch_length, segment_length, 
                     segment_shift, sample_period, zeropad, average_segments):
        """
        Returns the shape of the main result and the average over epochs
        """
        # this is useless here unless the input could actually be a 2D timeseries
        nchan = numpy.where(len(input_shape) > 2, input_shape[2], input_shape[1])
        seg_tpts = segment_length / sample_period
        seg_shift_tpts = segment_shift / sample_period
        tpts  = numpy.where(epoch_length > 0.0, epoch_length / sample_period, input_shape[0])
        nfreq = numpy.min([max_freq, numpy.floor((seg_tpts + zeropad) / 2.0) + 1])
        #nep   = int(numpy.floor(input_shape[0] / epoch_length))
        nseg  = int(numpy.floor((tpts - seg_tpts) / seg_shift_tpts) + 1)

        if not average_segments:
            result_shape = (nchan, nchan, nfreq, nseg)
            av_result_shape = (nchan, nfreq, nseg)
        else: 
            result_shape = (nchan, nchan, nfreq)
            av_result_shape = (nchan, nfreq)
                        
        return [result_shape, av_result_shape]
    
    
    def result_size(self, input_shape, max_freq, epoch_length, segment_length, 
                     segment_shift, sample_period, zeropad, average_segments):
        """
        Returns the storage size in Bytes of the main result (complex array) of 
        the ComplexCoherence
        """
        result_size = numpy.prod(self.result_shape(input_shape, max_freq, 
                                                   epoch_length, segment_length,
                                                   segment_shift, sample_period, 
                                                   zeropad, average_segments)[0])* 2.0 * 8.0 #complex*Bytes
        return result_size
    
    
    def extended_result_size(self, input_shape, max_freq, epoch_length, segment_length, 
                             segment_shift, sample_period, zeropad, average_segments):
        """
        Returns the storage size in Bytes of the extended result of the ComplexCoherence. 
        That is, it includes storage of the evaluated ComplexCoherence attributes
        such as ...
        """
        result_shape = self.result_shape(input_shape, max_freq, epoch_length, 
                                         segment_length, segment_shift, 
                                         sample_period, zeropad, average_segments)[0]
        result_size = self.result_size(input_shape, max_freq, epoch_length, 
                                       segment_length, segment_shift, 
                                       sample_period, zeropad, average_segments)
        extend_size = result_size * 2.0 #Main arrays: cross spectrum and complex coherence
        extend_size = extend_size + result_shape[2] * 8.0  #Frequency
        extend_size = extend_size + 8.0 # Epoch length
        extend_size = extend_size + 8.0 # Segment length
        return extend_size
