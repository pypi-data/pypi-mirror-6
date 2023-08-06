''' Bridge to EMAN2 with asorted utilities

This module handles testing for and converting EMAN2 objects to
numpy arrays.

.. Created on Sep 28, 2010
.. codeauthor:: Robert Langlois <rl2528@columbia.edu>
'''

from ..app import tracing
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


try:
    import EMAN2
    import utilities
    import fundamentals
    EMAN2;
    fundamentals;
    utilities;
except:
    tracing.log_import_error('Failed to load EMAN2 module', _logger)
    EMAN2 = None
    fundamentals = None 
    utilities = None
import numpy


def is_avaliable():
    ''' Test if EMAN2 is available
    
    :Returns:
    
    out : bool
          True if the EMAN2 library is available
    '''
    
    return EMAN2 is not None


def fshift(img, x, y, z=0, out=None):
    ''' Shift an image
    
    * has alternative
    
    :Parameters:
    
    img : array
          Image data
    x : float
        Translation in the x-direction
    y : float
        Translation in the y-direction
    z : float
        Translation in the z-direction
    out : array
          Output array
        
    :Returns:
    
    img : array
          Transformed image
    '''
    
    if fundamentals is None: raise ImportError, "EMAN2/Sparx library not available, fshift requires EMAN2/Sparx"
    if out is None: out = img.copy()
    emdata = numpy2em(img)
    emdata = fundamentals.fshift(emdata, x, y, z)
    out[:, :] = em2numpy(emdata)
    return out

def normalize_mask(img, mask, no_std=0, out=None):
    ''' Mirror an image about the x-axis
    
    * has alternative
    
    :Parameters:
    
    img : array
          Image data
    mask : array
           Mask
    out : array
          Output array
        
    :Returns:
    
    img : array
          Transformed image
    '''
    
    if EMAN2 is None: raise ImportError, "EMAN2/Sparx library not available, normalize_mask requires EMAN2/Sparx"
    if out is None: out = img.copy()
    emdata = numpy2em(img)
    emdata.process_inplace("normalize.mask", {"mask": numpy2em(mask), "no_sigma": no_std})
    out[:, :] = em2numpy(emdata)
    return out

def mirror(img, out=None):
    ''' Mirror an image about the x-axis
    
    * has alternative
    
    :Parameters:
    
    img : array
          Image data
    out : array
          Output array
        
    :Returns:
    
    img : array
          Transformed image
    '''
    
    if EMAN2 is None: raise ImportError, "EMAN2/Sparx library not available, mirror requires EMAN2/Sparx"
    if out is None: out = img.copy()
    emdata = numpy2em(img)
    emdata.process_inplace("mirror", {"axis":'x'})
    out[:, :] = em2numpy(emdata)
    return out

def rot_shift2D(img, psi, tx=None, ty=None, m=None, out=None):
    ''' Rotate and shift an image in 2D
    
    
    * has alternative
    
    :Parameters:
    
    img : array
          Image data
    psi : float
          Inplane rotation
    tx : int
         Translation in the x-direction
    ty : int
         Translation in the y-direction
    m : bool
        True if image should be mirrored around x-axis
    out : array
          Output array
        
    :Returns:
    
    img : array
          Transformed image
    '''
    
    if fundamentals is None: raise ImportError, "EMAN2/Sparx library not available, rot_shift2D requires EMAN2/Sparx"
    if tx is None:
        #m = psi[1] > 179.9
        tx = psi[6]
        ty = psi[7]
        psi = psi[5]
    if out is None: out = img.copy()
    emdata = numpy2em(img)
    emdata = fundamentals.rot_shift2D(emdata, psi, tx, ty, m, interpolation_method="gridding")
    out[:, :] = em2numpy(emdata)
    return out

def model_circle(rad, x, y):
    ''' Create a model circle
    
    * has alternative
    
    :Parameters:
    
    rad : int
          Radius
    x : int
        Width of the image
    y : int
        Height of the image
        
    :Returns:
    
    model : array
            Image with disk of radius `rad`
    '''
    
    if utilities is None: raise ImportError, "EMAN2/Sparx library not available, model_circle requires EMAN2/Sparx"
    emdata =  utilities.model_circle(rad, x, y)
    return em2numpy(emdata).copy()

def em2numpy2em(fn):
    ''' Convert the first argument from EMData to ndarray and convert result
    from ndarray to EMData only if the input is EMData.
    
    :Parameters:
    
    fn : function
         Name of the function to decorate
    
    :Returns:
    
    new : function
          Decorator
    '''
    
    def new(img, *args, **kwargs):
        '''Convert the first argument from EMData to ndarray and convert result
        from ndarray to EMData only if the input is EMData.
        
        :Parameters:
            
        img : EMData or ndarray
              Image
        args : list
               Other positional arguments
        kwargs : dict
                 Other keyword arguments
        
        :Returns:
        
        img : EMData or ndarray (depending on input)
              Image
        '''
        
        if EMAN2 is None: return fn(img, *args, **kwargs)
        orig = img
        if is_em(img): img = em2numpy(img)
        res = fn(img, *args, **kwargs)
        if is_em(orig): res = numpy2em(res)
        return res
    return new

def em2numpy2res(fn):
    ''' Convert the first argument from EMData to ndarray and convert result
    from ndarray to EMData only if the input is EMData.
    
    :Parameters:
    
    fn : function
         Name of the function to decorate
    
    :Returns:
    
    new : function
          Decorator
    '''
    
    def new(img, *args, **kwargs):
        '''Convert the first argument from EMData to ndarray and convert result
        from ndarray to EMData only if the input is EMData.
        
        :Parameters:
            
        img : EMData or ndarray
              Image
        args : list
               Other positional arguments
        kwargs : dict
                 Other keyword arguments
        
        :Returns:
        
        img : EMData or ndarray (depending on input)
              Image
        '''
        
        if EMAN2 is None: return fn(img, *args, **kwargs)
        orig = img
        orig;
        if is_em(img): img = em2numpy(img)
        res = fn(img, *args, **kwargs)
        return res
    return new

def is_em(im):
    '''Test if image is an EMAN2 image (EMData)
    
    This convenience method tests if the image is an EMAN2 image (EMAN2.EMData)
    
    .. sourcecode:: py
        
        >>> from core.image.eman2_utility import *
        >>> is_em(numpy.zeros((20,20)))
        False
        >>> is_em(EMData())
        True
    
    :Parameters:

    img : image-like object
         A object holding an image possibly EMAN2.EMData
        
    :Returns:
        
    return_val : boolean
                True if it is an EMAN2 image (EMAN2.EMData)
    '''
    
    return isinstance(im, EMAN2.EMData)

def is_numpy(im):
    '''Test if image is a NumPy array
    
    This convenience method tests if the image is a numpy.ndarray.
    
    .. sourcecode:: py
    
        >>> from core.image.eman2_utility import *
        >>> is_em(numpy.zeros((20,20)))
        True
        >>> is_em(EMData())
        False
    
    :Parameters:

    img : image-like object
         A object holding an image possibly numpy.ndarray
        
    :Returns:
        
    return_val : boolean
                True if is a numpy.ndarray
    '''
    
    return isinstance(im, numpy.ndarray)

def em2numpy(im):
    '''Convert EMAN2 image object to a NumPy array
    
    This convenience method converts an EMAN2.EMData object into a numpy.ndarray.
    
    .. sourcecode:: py
    
        >>> from core.image.eman2_utility import *
        >>> e = EMData()
        >>> e.set_size(2, 2, 1)
        >>> e.to_zero()
        >>> em2numpy(e)
        array([[ 0.,  0.],
               [ 0.,  0.]], dtype=float32)
    
    :Parameters:

    img : EMAN2.EMData
         An image object
        
    :Returns:
        
    return_val : numpy.ndarray
                An numpy.ndarray holding image data
    '''
    
    if EMAN2 is None: raise ImportError, "EMAN2/Sparx library not available, numpy2em requires EMAN2/Sparx"
    return EMAN2.EMNumPy.em2numpy(im)

def numpy2em(im, e=None):
    '''Convert NumPy array to an EMAN2 image object
    
    This convenience method converts a numpy.ndarray object into an EMAN2.EMData
    
    .. sourcecode:: py
    
        >>> from core.image.eman2_utility import *
        >>> ar = numpy.zeros((2,2))
        >>> numpy2em(ar)
        <libpyEMData2.EMData object at 0xdd61b0>
    
    :Parameters:

    img : numpy.ndarray
          A numpy array
        
    :Returns:
        
    return_val : EMAN2.EMData
                An EMAN2 image object
    '''
        
    if EMAN2 is None: raise ImportError, "EMAN2/Sparx library not available, numpy2em requires EMAN2/Sparx"
    try:
        im = numpy.require(im, numpy.float32)
        if e is None: e = EMAN2.EMData()
        EMAN2.EMNumPy.numpy2em(im, e)
        return e
    except:
        return EMAN2.EMNumPy.numpy2em(im)

def fsc(img1, img2, complex=False):
    ''' Estimate the Fourier shell correlation between two images
    
    :Parameters:
    
    img1 : array
           Image
    img2 : array
           Image
    complex : bool
              Set true if images are complex - preventative care
    
    :Returns:
    
    fsc : array
          Fourier shell correlation curve: (0) spatial frequency (1) FSC
    '''
    
    if EMAN2 is None: raise ImportError, "EMAN2/Sparx library not available, fsc requires EMAN2/Sparx"
    if not is_em(img1): img1 = numpy2em(img1)
    if not is_em(img2): img2 = numpy2em(img2)
    if complex:
        img1.set_attr('is_complex', 1)
        img2.set_attr('is_complex', 1)
    res = img1.calc_fourier_shell_correlation(img2, 1.0)
    res = numpy.asarray(res).reshape((3, len(res)/3)).T
    #sel = numpy.abs(res[:, 1]-0.5)
    #sp = res[sel.argmin(), 0]
    #resolution = apix*bin_factor/sp
    return res

def ramp(img, inplace=True):
    '''Remove change in illumination across an image
    
    :Parameters:

    img : EMAN2.EMData
          Input Image
    inplace : bool
              If True, process the image in place.
    
    :Returns:
    
    img : EMAN2.EMData
          Ramped Image
    '''
    
    if EMAN2 is None: raise ImportError, "EMAN2/Sparx library not available, ramp requires EMAN2/Sparx"
    orig = img
    if not is_em(img): img = numpy2em(img)
    if inplace: img.process_inplace("filter.ramp")
    else: img = img.process("filter.ramp")
    if not is_em(orig): 
        if inplace:
            orig[:]=em2numpy(img)
            return orig
        else:
            img = em2numpy(img).copy()
    return img

def histfit(img, mask, noise, debug=False):
    '''Contrast enhancement using histogram fitting (ce_fit in Spider).
    
    :Parameters:
        
    img : EMAN2.EMData
          Input Image
    mask : EMAN2.EMData
           Image mask
    noise : EMAN2.EMData
            Noise image
    
    :Returns:

    out : EMAN2.EMData
          Enhanced image
    '''
    
    if EMAN2 is None: raise ImportError, "EMAN2/Sparx library not available, histfit requires EMAN2/Sparx"
    if debug:
        info, tag, img = utilities.ce_fit(img, noise, mask)
        print info, tag
        return img
    else:
        return utilities.ce_fit(img, noise, mask)[2]
    
def decimate(img, bin_factor=0, force_even=False, **extra):
    '''Decimate the image
    
    :Parameters:

    img : EMAN2.EMData
          Image to decimate
    bin_factor: int
                Factor to decimate
    force_even: bool
                Ensure decimated image has even dimensions
    extra : dict
            Unused extra keyword arguments
    
    :Returns:

    val : EMAN2.EMData
          Decimated image
    '''
    
    if EMAN2 is None: raise ImportError, "EMAN2/Sparx library not available, decimate requires EMAN2/Sparx"
    orig = img
    if not is_em(img): img = numpy2em(img)
    
    if bin_factor == 0.0: return img
    bin_factor = 1.0/bin_factor
    
    if force_even:
        n = int( float(img.get_xsize()) * bin_factor )
        if (n % 2) > 0:
            n += 1
            bin_factor = float(n) / float(img.get_xsize())
    
    frequency_cutoff = 0.5*bin_factor
    template_min = 15
    sb = EMAN2.Util.sincBlackman(template_min, frequency_cutoff, 1999) # 1999 taken directly from util_sparx.h
    img = img.downsample(sb, bin_factor)
    if not is_em(orig): 
        orig = img
        img = em2numpy(orig).copy()
    return img

def butterworth_low_pass(img, bw_lo, bw_falloff, pad=False, **extra):
    ''' Filter an image with the Gaussian high pass filter
    
    :Parameters:

    img : EMAN2.EMData
          Image requiring filtering
    ghp_sigma : float
                Frequency range
    pad : bool
          Pad image
    extra : dict
            Unused extra keyword arguments
    
    :Returns:

    val : EMAN2.EMData
          Filtered image
    '''
    
    if EMAN2 is None: raise ImportError, "EMAN2/Sparx library not available, butterworth_low_pass requires EMAN2/Sparx"
    orig = img
    if not is_em(img): img = numpy2em(img)
    img = EMAN2.Processor.EMFourierFilter(img, {"filter_type" : EMAN2.Processor.fourier_filter_types.BUTTERWORTH_LOW_PASS,    "low_cutoff_frequency": bw_lo, "high_cutoff_frequency": bw_lo+bw_falloff, "dopad" : pad})
    if not is_em(orig): img = em2numpy(img).copy()
    return img

def butterworth_high_pass(img, bw_hi, bw_falloff, pad=False, **extra):
    ''' Filter an image with the Gaussian high pass filter
    
    :Parameters:

    img : EMAN2.EMData
          Image requiring filtering
    ghp_sigma : float
                Frequency range
    pad : bool
          Pad image
    extra : dict
            Unused extra keyword arguments
    
    :Returns:

    val : EMAN2.EMData
          Filtered image
    '''
    
    if EMAN2 is None: raise ImportError, "EMAN2/Sparx library not available, butterworth_high_pass requires EMAN2/Sparx"
    orig = img
    if not is_em(img): img = numpy2em(img)
    img = EMAN2.Processor.EMFourierFilter(img, {"filter_type" : EMAN2.Processor.fourier_filter_types.BUTTERWORTH_HIGH_PASS,   "low_cutoff_frequency": bw_hi+bw_falloff, "high_cutoff_frequency": bw_hi, "dopad" : pad})
    if not is_em(orig): img = em2numpy(img).copy()
    return img

def butterworth_band_pass(img, bw_lo, bw_hi, bw_falloff, pad=False, **extra):
    ''' Filter an image with the Gaussian high pass filter
    
    :Parameters:

    img : EMAN2.EMData
          Image requiring filtering
    ghp_sigma : float
                Frequency range
    pad : bool
          Pad image
    extra : dict
            Unused extra keyword arguments
    
    :Returns:

    val : EMAN2.EMData
          Filtered image
    '''
    
    if EMAN2 is None: raise ImportError, "EMAN2/Sparx library not available, butterworth_band_pass requires EMAN2/Sparx"
    orig = img
    if not is_em(img): img = numpy2em(img)
    img = EMAN2.Processor.EMFourierFilter(img, {"filter_type" : EMAN2.Processor.fourier_filter_types.BUTTERWORTH_HIGH_PASS,   "low_cutoff_frequency": bw_hi+bw_falloff, "high_cutoff_frequency": bw_hi, "dopad" : pad})
    img = EMAN2.Processor.EMFourierFilter(img, {"filter_type" : EMAN2.Processor.fourier_filter_types.BUTTERWORTH_LOW_PASS,    "low_cutoff_frequency": bw_lo, "high_cutoff_frequency": bw_lo+bw_falloff, "dopad" : pad})
    if not is_em(orig): img = em2numpy(img).copy()
    return img

def gaussian_high_pass(img, ghp_sigma=0.1, pad=False, **extra):
    ''' Filter an image with the Gaussian high pass filter
    
    :Parameters:

    img : EMAN2.EMData
          Image requiring filtering
    ghp_sigma : float
                Frequency range
    pad : bool
          Pad image
    extra : dict
            Unused extra keyword arguments
    
    :Returns:

    val : EMAN2.EMData
          Filtered image
    '''
    
    if EMAN2 is None: raise ImportError, "EMAN2/Sparx library not available, gaussian_high_pass requires EMAN2/Sparx"
    if ghp_sigma == 0.0: return img
    orig = img
    if not is_em(img): img = numpy2em(img)
    img = EMAN2.Processor.EMFourierFilter(img, {"filter_type" : EMAN2.Processor.fourier_filter_types.GAUSS_HIGH_PASS,   "cutoff_abs": ghp_sigma, "dopad" : pad})
    if not is_em(orig): img = em2numpy(img).copy()
    return img

def gaussian_low_pass(img, glp_sigma=0.1, pad=False, **extra):
    ''' Filter an image with the Gaussian low pass filter
    
    :Parameters:

    img : EMAN2.EMData
          Image requiring filtering
    glp_sigma : float
                Frequency range
    pad : bool
          Pad image
    extra : dict
            Unused extra keyword arguments
    
    :Returns:

    val : EMAN2.EMData
          Filtered image
    '''
    
    if EMAN2 is None: raise ImportError, "EMAN2/Sparx library not available, gaussian_low_pass requires EMAN2/Sparx"
    if glp_sigma == 0.0: return img
    orig = img
    if not is_em(img): img = numpy2em(img)
    img = EMAN2.Processor.EMFourierFilter(img, {"filter_type" : EMAN2.Processor.fourier_filter_types.GAUSS_LOW_PASS,    "cutoff_abs": glp_sigma, "dopad" : pad})
    if not is_em(orig): img = em2numpy(img).copy()
    return img

def setup_nn4(image_size, npad=2, sym='c1', weighting=1, **extra):
    ''' Initalize a reconstruction object
    
    :Parameters:
    
    image_size : int
                 Size of the input image and output volume
    npad : int, optional
           Number of times to pad the input image, default: 2
    sym : str, optional
          Type of symmetry, default: 'c1'
    weighting : int
                Amount of weight to give projections
    
    :Returns:
    
    recon : tuple
            Reconstructor, Fourier volume, Weight Volume, and numpy versions
    '''
    
    if EMAN2 is None: raise ImportError, "EMAN2/Sparx library not available, setup_nn4 requires EMAN2/Sparx"
    fftvol = EMAN2.EMData()
    weight = EMAN2.EMData()
    param = {"size":image_size, "npad":npad, "symmetry":sym, "weighting":weighting, "fftvol": fftvol, "weight": weight}
    r = EMAN2.Reconstructors.get("nn4", param)
    r.setup()
    return (r, fftvol, weight), em2numpy(fftvol), em2numpy(weight), image_size

def backproject_nn4_queue(qin, qout, shmem, shape, process_limit, process_number, align=None, **extra):
    ''' Add the given image and alignment or generator of image/alignment pairs
    to the current reconstruction
    
    :Parameters:
    
    img : array or EMData
          Image of projection to backproject into reconstruction
    align : array, optional
            Array of alignment parameters (not required if img is generator of images and alignments)
    recon : tuple
            Reconstructor, Fourier volume, Weight Volume, and numpy versions
    extra : dict
            Keyword arguments to be passed to setup_nn4 if recon is None
    
    :Returns:
    
    recon : tuple
            Reconstructor, Fourier volume, Weight Volume, and numpy versions
    '''
    
    if EMAN2 is None: raise ImportError, "EMAN2/Sparx library not available, backproject_nn4_queue requires EMAN2/Sparx"
    npad, sym, weighting = extra.get('npad', 2), extra.get('sym', 'c1'), extra.get('weighting', 1)
    e = EMAN2.EMData()
    recon=None
    while True:
        pos = qin.get()
        if pos is None or pos[0] == -1: 
            if hasattr(qin, "task_done"):  qin.task_done()
            break
        pos, idx = pos
        a = align[idx]
        img = shmem[pos].reshape(shape)
        xform_proj = EMAN2.Transform({"type":"spider","phi":a[2],"theta":a[1],"psi":a[0]})
        if not is_em(img): img = numpy2em(img, e)
        if recon is None: recon = setup_nn4(img.get_xsize(), npad, sym, weighting)
        recon[0][0].insert_slice(img, xform_proj)
        qout.put((process_number, idx))
    return recon[0], recon[1], recon[2]

def backproject_nn4_new(img, align=None, recon=None, **extra):
    ''' Add the given image and alignment or generator of image/alignment pairs
    to the current reconstruction
    
    :Parameters:
    
    img : array or EMData
          Image of projection to backproject into reconstruction
    align : array, optional
            Array of alignment parameters (not required if img is generator of images and alignments)
    recon : tuple
            Reconstructor, Fourier volume, Weight Volume, and numpy versions
    extra : dict
            Keyword arguments to be passed to setup_nn4 if recon is None
    
    :Returns:
    
    recon : tuple
            Reconstructor, Fourier volume, Weight Volume, and numpy versions
    '''
    
    if EMAN2 is None: raise ImportError, "EMAN2/Sparx library not available, backproject_nn4_new requires EMAN2/Sparx"
    npad, sym, weighting = extra.get('npad', 2), extra.get('sym', 'c1'), extra.get('weighting', 1)
    e = EMAN2.EMData()
    if not hasattr(img, 'ndim'):
        for i, val in img:
            a = align[i]
            '''
            if a[4] != (i+1):
                _logger.error("mismatch: %d != %d -- %s"%(a[4], i+1, str(align[:5])))
            assert(a[4]==(i+1))
            '''
            xform_proj = EMAN2.Transform({"type":"spider","phi":a[2],"theta":a[1],"psi":a[0]})
            if not is_em(val): val = numpy2em(val, e)
            if recon is None: recon = setup_nn4(val.get_xsize(), npad, sym, weighting)
            recon[0][0].insert_slice(val, xform_proj)
    else:
        xform_proj = EMAN2.Transform({"type":"spider","phi":align[2],"theta":align[1],"psi":align[0]})
        if not is_em(img):img = numpy2em(img)
        if recon is None: recon = setup_nn4(val.get_xsize(), npad, sym, weighting)
        recon[0][0].insert_slice(img, xform_proj)
    val1 = recon[1].copy()
    val2 = recon[2].copy()
    return val1, val2
    
def backproject_nn4(img, align=None, recon=None, **extra):
    ''' Add the given image and alignment or generator of image/alignment pairs
    to the current reconstruction
    
    :Parameters:
    
    img : array or EMData
          Image of projection to backproject into reconstruction
    align : array, optional
            Array of alignment parameters (not required if img is generator of images and alignments)
    recon : tuple
            Reconstructor, Fourier volume, Weight Volume, and numpy versions
    extra : dict
            Keyword arguments to be passed to setup_nn4 if recon is None
    
    :Returns:
    
    recon : tuple
            Reconstructor, Fourier volume, Weight Volume, and numpy versions
    '''
    
    if EMAN2 is None: raise ImportError, "EMAN2/Sparx library not available, backproject_nn4 requires EMAN2/Sparx"
    npad, sym, weighting = extra.get('npad', 2), extra.get('sym', 'c1'), extra.get('weighting', 1)
    if not hasattr(img, 'ndim'):
        for i, val in enumerate(img):
            if isinstance(val, tuple): val, a = val
            else: a = align[i]
            xform_proj = EMAN2.Transform({"type":"spider","phi":a[2],"theta":a[1],"psi":a[0]})
            if not is_em(val): val = numpy2em(val)
            if recon is None: recon = setup_nn4(val.get_xsize(), npad, sym, weighting)
            recon[0][0].insert_slice(val, xform_proj)
    else:
        xform_proj = EMAN2.Transform({"type":"spider","phi":align[2],"theta":align[1],"psi":align[0]})
        if not is_em(img):img = numpy2em(img)
        if recon is None: recon = setup_nn4(val.get_xsize(), npad, sym, weighting)
        recon[0][0].insert_slice(img, xform_proj)
    return recon

def finalize_nn4(recon, recon2=None, npad=2, sym='c1', weighting=1):
    ''' Inverse Fourier transform the Fourier volume
    
    :Parameters:
    
    recon : tuple
            Reconstructor, Fourier volume, Weight Volume, and numpy versions
    
    :Returns:
    
    vol : array
          Volume as a numpy array
    '''
    
    if EMAN2 is None: raise ImportError, "EMAN2/Sparx library not available, finalize_nn4 requires EMAN2/Sparx"
    if recon2 is not None:
        fftvol = recon[1]+recon2[1]
        weight = recon[2]+recon2[2]
        fftvol = numpy2em(fftvol)
        weight = numpy2em(weight)
        param = {"size":recon[3], "npad":npad, "symmetry":sym, "weighting":weighting, "fftvol": fftvol, "weight": weight}
        r = EMAN2.Reconstructors.get("nn4", param)
        r.setup()
        return em2numpy(r.finish()).copy()
    
    if isinstance(recon, tuple): recon = recon[0]
    if isinstance(recon, tuple): recon = recon[0]
    return em2numpy(recon.finish()).copy()

