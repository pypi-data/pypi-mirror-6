''' Rotate a 2D projection

.. Created on Mar 19, 2013
.. codeauthor:: Robert Langlois <rl2528@columbia.edu>
'''
from ..app import tracing
import logging, numpy


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

try: 
    from spi import _spider_rotate
    _spider_rotate;
except:
    _spider_rotate=None
    _logger.exception("Module failed to load")
    tracing.log_import_error('Failed to load _spider_rotate.so module', _logger)
    
    
def rotate_image2(img, ang, tx=0.0, ty=0.0, out=None, scale=1.0):
    '''
    '''
    
    if out is None: out = img.copy(order='F')
    if not numpy.isfortran(img): img = numpy.asfortranarray(img)
    _spider_rotate.rotate_image(img, out, ang, scale, tx, ty)
    return numpy.ascontiguousarray(out)
    #return out

def rotate_image(img, ang, tx=0.0, ty=0.0, out=None, scale=1.0):
    '''
    '''
    
    if hasattr(ang, '__iter__'):
        tx = ang[6]
        ty = ang[7]
        ang = ang[5]
    
    if out is None: out = img.copy()
    _spider_rotate.rotate_image(img.T, out.T, ang, scale, tx, ty)
    return out

def rotate_euler(ref, ang, out=None):
    '''
    '''
    
    if hasattr(ang, 'ndim') and ang.ndim > 1 and ang.shape[1] == 3:
        out = ang.copy()
        for i in xrange(len(ang)):
            out[i] = rotate_euler(ref, ang[i])
        return out
    
    ref = numpy.asarray(ref, dtype=numpy.float32)
    ang = numpy.asarray(ang, dtype=numpy.float32)
    if out is None: out = ang.copy()
    _spider_rotate.rotate_euler(ref.T, ang.T, out.T)
    return out

def optimal_inplane(ref, ang, out=None):
    '''
    '''
    
    if ang.ndim > 1:
        ref = numpy.asarray(ref, dtype=numpy.float32)
        if out is None:out = numpy.zeros(len(ang))
        for i in xrange(len(ang)):
            tmp = rotate_euler(ref, ang[i])
            out[i] = -(tmp[0]+tmp[2])
        return out
    elif ref.ndim > 1:
        ang = numpy.asarray(ang, dtype=numpy.float32)
        if out is None:out = numpy.zeros(len(ref))
        for i in xrange(len(ref)):
            tmp = rotate_euler(ref[i], ang)
            out[i] = -(tmp[0]+tmp[2])
        return out
    else:
        rang = rotate_euler(ref, ang)
        if out is None:
            return -(rang[0]+rang[2])
        else:
            out[0]=-(rang[0]+rang[2])
            return out
        


