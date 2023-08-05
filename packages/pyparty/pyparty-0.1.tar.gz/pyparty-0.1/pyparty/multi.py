import copy
import numpy as np
import logging
import skimage.morphology as morphology
from pyparty.tools import ParticleManager, Canvas
from pyparty.utils import UtilsError

logger = logging.getLogger(__name__) 

class UtilsImportError(UtilsError):
    """ """

def multi_mask(ndarray, *masknames, **kwargs):
    """ Return dictionary of boolean masks corresponding to bins of colors
    in an image.

    Parmaters
    ---------
    *masknames : strings
        Name keys for output; otherwise, boolean arrays are keyed by the
        value returned by np.unique (float or int)
        
    ignore : int (0)
        Values/bins to ignore.  Defaults to 0 since that is usually the background
        of an ndarry.  Ignores by values not index, so ignore=0,1,2 would not 
        necessarily ignore the first three masks.
    
    sort : bool
        On dictionary return, collections.OrderedDict will be returned"""
    
    ignore = kwargs.pop('ignore', 0)
    sort = kwargs.pop('sort', True)
    
    if ndarray.ndim == 3:
        ndarray = rgb2uint(ndarray)
        logger.warn('multi_mask() converting 3-channel to 1-channel 8bit')

    unique = np.unique(ndarray)    

    if ignore is not None:
        if not hasattr(ignore, '__iter__'):
            ignore = [ignore]    

    # Did user pass invalid "ignore" values
    missing = [str(x) for x in ignore if x not in unique]
    if missing:
        if len(missing) < 6:
            logger.warn('intensities %s were set to be ignored but were ' 
                'not found in image pixel values' % missing)            
        else:
            logger.warn('%s pixel intensities were set to be ignored but were ' 
                'not found in image pixel values' % len(missing))


    unique = [x for x in unique if x not in ignore]
    
    if sort:
        try:
            from collections import OrderedDict
        except ImportError:
            raise UtilsImportError('Sorting requires OrderedDict form '
                'python.collection package; package is standard in 2.7 and '
                'higher')        
        out = OrderedDict()
    else:
        out = {}
    
    if masknames:
        if len(masknames) != len(unique):
            logger.warn('length mismatch in unique colors (%s) and masknames '
                        '(%s)' % (len(unique), len(masknames)) )
    
    for idx, value in enumerate(unique):
        try:
            key = masknames[idx]
        except IndexError:
            key = value
        out[key] = (ndarray == unique[idx])        
    return out


def multi_labels(masks, as_canvas=True, prefix=True, neighbors=4, **pmankwargs):
    """ Wraps Particles.from_labels() for elements in list/dict of
    BOOLEAN mask arrays."""
        
    if isinstance(masks, dict):
        out = copy.copy(masks) # to preserve sorting
        
        for name, image in masks.items():
            if image.dtype != bool:
                raise UtilsError('multi_labels() requires boolean arrays')
            labels = morphology.label(image, background=False, neighbors=neighbors)
            
            if prefix:
                if prefix == True:
                    _prefix = name
                particles = ParticleManager.from_labels(labels, prefix=_prefix, 
                                                        **pmankwargs) 
            else:
                particles = ParticleManager.from_labels(labels, **pmankwargs)        
                
            if not as_canvas:
                out[name] = particles
            else:
                c = Canvas(particles=particles)
                c.rez = image.shape #Bug when initializing with rez and no bg
                out[name] = c
        
    # If masks is a list
    else:
        if not hasattr(masks, '__iter__'):
            masks = [masks]
        out = []

        for image in masks:
            labels = morphology.label(image, neighbors=neighbors)
            particles = ParticleManager.from_labels(labels, **pmankwargs)

            if not as_canvas:
                out.append(particles)
            else:
                c= Canvas(particles=particles)
                c.rez = image.shape
                out.append(c)
    return out  
            