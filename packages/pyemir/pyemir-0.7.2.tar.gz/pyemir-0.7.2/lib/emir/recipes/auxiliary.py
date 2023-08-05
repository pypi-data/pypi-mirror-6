#
# Copyright 2011-2012 Universidad Complutense de Madrid
# 
# This file is part of PyEmir
# 
# PyEmir is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PyEmir is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PyEmir.  If not, see <http://www.gnu.org/licenses/>.
#

'''Auxiliary Recipes for EMIR'''

import logging

import numpy
import pyfits
from numina.core import RecipeError
from numina.core import BaseRecipe, RecipeRequirements, DataFrame
from numina.core import Requirement, Product, DataProductRequirement
from numina.core import define_requirements, define_result
from numina.logger import log_to_history
from numina.array.combine import median
from numina import __version__
from numina.flow import SerialFlow
from numina.flow.node import IdNode
from numina.flow.processing import BiasCorrector
from numina.flow.processing import DarkCorrector, NonLinearityCorrector, BadPixelCorrector

from emir.core import RecipeResult
from emir.dataproducts import MasterBias, MasterDark, MasterBadPixelMask
from emir.dataproducts import NonLinearityCalibration, MasterIntensityFlat
from emir.dataproducts import WavelengthCalibration, MasterSpectralFlat
from emir.dataproducts import SlitTransmissionCalibration, ChannelLevelStatistics

__all__ = ['BiasRecipe', 'DarkRecipe', 'IntensityFlatRecipe',
           'SpectralFlatRecipe', 'SlitTransmissionRecipe',
           'WavelengthCalibrationRecipe']

_logger = logging.getLogger('numina.recipes.emir')

_s_author = "Sergio Pascual <sergiopr@fis.ucm.es>"

class BiasRecipeRequirements(RecipeRequirements):
    master_bpm = DataProductRequirement(MasterBadPixelMask, 'Master bad pixel mask')

class BiasRecipeResult(RecipeResult):
    biasframe = Product(MasterBias)
    stats = Product(ChannelLevelStatistics)

@define_requirements(BiasRecipeRequirements)
@define_result(BiasRecipeResult)
class BiasRecipe(BaseRecipe):
    '''
    Recipe to process data taken in Bias image Mode.

    Bias images only appear in Simple Readout mode.

    **Observing modes:**
    
     * Bias Image (3.1)   
    
    **Inputs:**
    
    **Outputs:**
    
     * A combined bias frame, with variance extension.
     * Statistics of the final image per channel (mean, median , variance) 
    
    **Procedure:**
    
    The list of images can be readly processed by combining them with a median algorithm.
    
    '''

    def __init__(self):
        super(BiasRecipe, self).__init__(author=_s_author,version="0.1.0")

    # FIXME find a better way of doing this automatically
    # @log_to_history(_logger)
    def run(self, obresult, reqs):
        _logger.info('starting bias reduction')

        cdata = []

        try:
            for frame in obresult.frames:
                hdulist = pyfits.open(frame.label, memmap=True, mode='readonly')
                cdata.append(hdulist)

            _logger.info('stacking %d images using median', len(cdata))
            
            data = median([d['primary'].data for d in cdata], dtype='float32')

            var2 = numpy.zeros_like(data[0])
            cls = ChannelLevelStatistics(exposure=0.0)
            for region in self.instrument.detector['channels']:
                mean = numpy.mean(data[0][region])
                med = numpy.median(data[0][region])
                var = numpy.var(data[0][region])
                stts = mean, med, var
                cls.statistics.append([region, stts])
                var2[region] = var

            hdu = pyfits.PrimaryHDU(data[0], header=cdata[0]['PRIMARY'].header)
    
            # update hdu header with
            # reduction keywords
            hdr = hdu.header
            #hdr.update('FILENAME', 'master_bias-%(block_id)d.fits' % self.environ)
            hdr.update('IMGTYP', 'BIAS', 'Image type')
            hdr.update('NUMTYP', 'MASTER_BIAS', 'Data product type')
            hdr.update('NUMXVER', __version__, 'Numina package version')
            hdr.update('NUMRNAM', self.__class__.__name__, 'Numina recipe name')
            hdr.update('NUMRVER', self.__version__, 'Numina recipe version')

            exhdr = pyfits.Header()
            exhdr.update('extver', 1)
            varhdu = pyfits.ImageHDU(data[1], name='VARIANCE', header=exhdr)
            exhdr = pyfits.Header()
            exhdr.update('extver', 2)
            var2hdu = pyfits.ImageHDU(var2, name='VARIANCE', header=exhdr)
            num = pyfits.ImageHDU(data[2], name='MAP')

            hdulist = pyfits.HDUList([hdu, varhdu, var2hdu, num])

            _logger.info('bias reduction ended')
            
            result = BiasRecipeResult(biasframe=DataFrame(hdulist),
                                      stats=cls)
            return result
        finally:
            for hdulist in cdata:
                hdulist.close()
            
class DarkRecipeRequirements(BiasRecipeRequirements):
    master_bias = DataProductRequirement(MasterBias, 'Master bias calibration', optional=True)

class DarkRecipeResult(RecipeResult):
    darkframe = Product(MasterDark)
    stats = Product(ChannelLevelStatistics)

@define_requirements(DarkRecipeRequirements)
@define_result(DarkRecipeResult)
class DarkRecipe(BaseRecipe):
    '''Recipe to process data taken in Dark current image Mode.

    Recipe to process dark images. The dark images will be combined 
    using the median.
    They do have to be of the same exposure time t.
    
    **Observing mode:**
    
     * Dark current Image (3.2)
    
    **Inputs:**
    
    **Outputs:**
    
     * A combined dark frame, with variance extension.
    ''' 

    def __init__(self):
        super(DarkRecipe, self).__init__(author=_s_author, version="0.1.0")
        
    # @log_to_history(_logger)
    def run(self, obresult, reqs):
        _logger.info('starting dark reduction')

        cdata = []
        expdata = []

        try:
                        
            for frame in obresult.frames:
                hdulist = pyfits.open(frame.label, memmap=True, mode='readonly')
                exposure = hdulist[0].header['EXPTIME']
                cdata.append(hdulist)
                expdata.append(exposure)

            if not all([exp == expdata[0] for exp in expdata]):
                _logger.error('image with wrong exposure time')
                raise RecipeError('image with wrong exposure time')

            _logger.info('stacking %d images using median', len(cdata))
            
            data = median([d['primary'].data for d in cdata], dtype='float32')
            hdu = pyfits.PrimaryHDU(data[0], header=cdata[0]['primary'].header)
            
        finally:
            for hdulist in cdata:
                hdulist.close()

        if reqs.master_bias is not None:
            # load bias
            
            master_bias = pyfits.open(reqs.master_bias, mode='readonly')
            _logger.info('subtracting bias %s', str(reqs.master_bias))
            # subtrac bias
            data[0] -= master_bias[0].data
            
            idx = master_bias.index_of(('variance', 1))
            data[1] += master_bias[idx].data
            

        var2 = numpy.zeros_like(data[0])

        cls = ChannelLevelStatistics(exposure=exposure)
        for region in self.instrument.detector['channels']:
            mean = numpy.mean(data[0][region])
            med = numpy.median(data[0][region])
            var = numpy.var(data[0][region])
            stts = mean, med, var
            cls.statistics.append([region, stts])
            var2[region] = var

        # update hdu header with
        # reduction keywords
        hdr = hdu.header
        hdr.update('NUMXVER', __version__, 'Numina package version')
        hdr.update('NUMRNAM', self.__class__.__name__, 'Numina recipe name')
        hdr.update('NUMRVER', self.__version__, 'Numina recipe version')
        
        #hdr.update('FILENAME', 'master_dark-%(block_id)d.fits' % self.environ)
        hdr.update('IMGTYP', 'DARK', 'Image type')
        hdr.update('NUMTYP', 'MASTER_DARK', 'Data product type')
        
        exhdr = pyfits.Header()
        exhdr.update('extver', 1)
        varhdu = pyfits.ImageHDU(data[1], name='VARIANCE', header=exhdr)
        exhdr = pyfits.Header()
        exhdr.update('extver', 2)
        var2hdu = pyfits.ImageHDU(var2, name='VARIANCE', header=exhdr)
        num = pyfits.ImageHDU(data[2], name='MAP')

        hdulist = pyfits.HDUList([hdu, varhdu, var2hdu, num])

        md = DataFrame(hdulist)

        _logger.info('dark reduction ended')
        result = DarkRecipeResult(darkframe=md,
                                      stats=cls)
        return result


class IntensityFlatRecipeRequirements(DarkRecipeRequirements):
    master_dark = DataProductRequirement(MasterDark, 'Master dark image')
    nonlinearity = DataProductRequirement(NonLinearityCalibration([1.0, 0.0]), 'Polynomial for non-linearity correction')

class IntensityFlatRecipeResult(RecipeResult):
    flatframe = Product(MasterIntensityFlat)

@define_requirements(IntensityFlatRecipeRequirements)
@define_result(IntensityFlatRecipeResult)
class IntensityFlatRecipe(BaseRecipe):
    '''Recipe to process data taken in intensity flat-field mode.
        
    Recipe to process intensity flat-fields. The flat-on and flat-off images are
    combined (method?) separately and the subtracted to obtain a thermal subtracted
    flat-field.
    
    **Observing modes:**
    
     * Intensity Flat-Field
    
    **Inputs:**
    
      * A master dark frame
      * Non linearity
      * A model of the detector. 
    
    **Outputs:**
    
     * TBD
    
    **Procedure:**
    
     * A combined thermal subtracted flat field, normalized to median 1, 
       with with variance extension and quality flag. 
    
    '''
    def __init__(self):
        super(IntensityFlatRecipe, self).__init__(
                        author=_s_author,
                        version="0.1.0"
                )
        
    #@log_to_history(_logger)
    def run(self, obresult, reqs):
        _logger.info('starting flat reduction')
                
        # Basic processing
        if reqs.master_bias:
            mbias = pyfits.getdata(reqs.master_bias)
            bias_corrector = BiasCorrector(mbias)
        else:
            bias_corrector = IdNode()
            
        mdark = pyfits.getdata(reqs.master_dark.label)
        dark_corrector = DarkCorrector(mdark)
        nl_corrector = NonLinearityCorrector(reqs.nonlinearity)
        
        
        basicflow = SerialFlow([bias_corrector, dark_corrector, nl_corrector])
        
        _logger.info('basic frame reduction')
        for frame in obresult.frames:

            with pyfits.open(frame.label, mode='update') as hdulist:
                hdulist = basicflow(hdulist)

        # combine LAMP-ON
        _logger.info('gathering LAMPON frames')
        lampon = [img.label for img in obresult.frames if img.itype == 'LAMPON']
        if not lampon:
            _logger.error('no LAMPON images in the ObservationResult')
            raise RecipeError('no LAMPON images in the ObservationResult')
        
        dataon = self.stack_images(lampon)
                
        # combine LAMP-OFF
        _logger.info('gathering LAMPOFF frames')
        lampoff = [img.label for img in obresult.frames if img.itype == 'LAMPOFF']
        if not lampoff:
            _logger.error('no LAMPOFF images in the ObservationResult')
            raise RecipeError('no LAMPOFF images in the ObservationResult')
        
        dataoff = self.stack_images(lampoff)
        
        # Subtract
        datafin = dataon[0] - dataoff[0]
        varfin = dataon[1] + dataoff[1]
        mapfin = dataon[2] + dataoff[2]

        meanval = datafin.mean()
        
        datafin /= meanval
        varfin /= (meanval * meanval)

        hdu = pyfits.PrimaryHDU(datafin)

        # update hdu header with
        # reduction keywords
        hdr = hdu.header
        hdr.update('NUMXVER', __version__, 'Numina package version')
        hdr.update('NUMRNAM', self.__class__.__name__, 'Numina recipe name')
        hdr.update('NUMRVER', self.__version__, 'Numina recipe version')
        
        #hdr.update('FILENAME', 'master_intensity_flat-%(block_id)d.fits' % self.environ)
        hdr.update('IMGTYP', 'FLAT', 'Image type')
        hdr.update('NUMTYP', 'MASTER_FLAT', 'Data product type')
        
        varhdu = pyfits.ImageHDU(varfin, name='VARIANCE')
        num = pyfits.ImageHDU(mapfin, name='MAP')

        hdulist = pyfits.HDUList([hdu, varhdu, num])

        md = DataFrame(hdulist)

        result = IntensityFlatRecipeResult(flatframe=md)

        return result
        
        
    def stack_images(self, images):
        
        cdata = []

        try:
            for name in images:
                hdulist = pyfits.open(name, memmap=True, mode='readonly')
                cdata.append(hdulist)

            _logger.info('stacking %d images using median', len(cdata))
            
            data = median([d['primary'].data for d in cdata], dtype='float32')
            return data
            
        finally:
            for hdulist in cdata:
                hdulist.close()
        
        
class SpectralFlatRecipeRequirements(IntensityFlatRecipeRequirements):
    pass

class SpectralFlatRecipeResult(RecipeResult):
    flatframe = Product(MasterSpectralFlat)

@define_requirements(SpectralFlatRecipeRequirements)
@define_result(SpectralFlatRecipeResult)
class SpectralFlatRecipe(BaseRecipe):
    '''Spectral Flatfield Recipe.

    Recipe to process spectral flat-fields. The flat-on and flat-off images are
    combined (method?) separately and the subtracted to obtain a thermal subtracted
    flat-field.

    **Observing modes:**

        * Multislit mask Flat-Field
     
    **Inputs:**

     * A list of lamp-on flats
     * A model of the detector 

    **Outputs:**

     * A combined spectral flat field with with variance extension and quality flag.

    **Procedure:**

     * TBD

    '''

    def __init__(self):
        super(SpectralFlatRecipe, self).__init__(
            author="Sergio Pascual <sergiopr@fis.ucm.es>",
            version="0.1.0"
        )

    def run(self, obresult, reqs):
        return SpectralFlatRecipeResult(flatframe=MasterSpectralFlat(None))

class SlitTransmissionRecipeRequirements(RecipeRequirements):
    master_bpm = DataProductRequirement(MasterBadPixelMask, 'Master bad pixel mask')
    master_bias = DataProductRequirement(MasterBias, 'Master bias image')
    master_dark = DataProductRequirement(MasterDark, 'Master dark image')
    nonlinearity = DataProductRequirement(NonLinearityCalibration([1.0, 0.0]), 'Polynomial for non-linearity correction')

class SlitTransmissionRecipeResult(RecipeResult):
    slit = Product(SlitTransmissionCalibration)

@define_requirements(SlitTransmissionRecipeRequirements)
@define_result(SlitTransmissionRecipeResult)
class SlitTransmissionRecipe(BaseRecipe):
    '''Recipe to calibrate the slit transmission.

    **Observing modes:**

        * Slit transmission calibration (4.4)
     
    **Inputs:**

        * A list of uniformly illuminated images of MSM

    **Outputs:**

     * A list of slit transmission functions 

    **Procedure:**

     * TBD

    '''

    def __init__(self):
        super(SlitTransmissionRecipe, self).__init__(
            author="Sergio Pascual <sergiopr@fis.ucm.es>",
            version="0.1.0"
        )

    @log_to_history(_logger)
    def run(self, obresult, reqs):
        return SlitTransmissionRecipeResult(slit=SlitTransmissionCalibration())

class WavelengthCalibrationRecipeRequirements(RecipeRequirements):
    master_bpm = DataProductRequirement(MasterBadPixelMask, 'Master bad pixel mask')
    master_bias = DataProductRequirement(MasterBias, 'Master bias image')
    master_dark = DataProductRequirement(MasterDark, 'Master dark image')
    nonlinearity = DataProductRequirement(NonLinearityCalibration([1.0, 0.0]), 'Polynomial for non-linearity correction')
    master_intensity_ff = DataProductRequirement(MasterIntensityFlat, 'Master intensity flatfield')
    master_spectral_ff = DataProductRequirement(MasterSpectralFlat, 'Master spectral flatfield')
        
class WavelengthCalibrationRecipeResult(RecipeResult):
    cal = Product(WavelengthCalibration)
        
@define_requirements(WavelengthCalibrationRecipeRequirements)
@define_result(WavelengthCalibrationRecipeResult)
class WavelengthCalibrationRecipe(BaseRecipe):
    '''Recipe to calibrate the spectral response.

    **Observing modes:**

        * Wavelength calibration (4.5)
     
    **Inputs:**

     * List of line positions
     * Calibrations upto spectral flatfielding

    **Outputs:**

     * Wavelength calibration structure 

    **Procedure:**

     * TBD
    '''

    def __init__(self):
        super(WavelengthCalibrationRecipe, self).__init__(
            author="Sergio Pascual <sergiopr@fis.ucm.es>",
            version="0.1.0"
        )

    @log_to_history(_logger)
    def run(self, obresult, reqs):
        return WavelengthCalibrationRecipeResult(cal=WavelengthCalibration())


