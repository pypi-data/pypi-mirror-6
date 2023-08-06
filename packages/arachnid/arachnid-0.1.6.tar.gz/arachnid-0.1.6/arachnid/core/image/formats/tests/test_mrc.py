''' Unit testing for the image formats

.. Created on Aug 31, 2012
.. codeauthor:: Robert Langlois <rl2528@columbia.edu>
'''

from .. import mrc, eman_format
import numpy, os #, sys

test_file = 'test.mrc'

def test_is_format_header():
    '''
    '''
    
    ar = numpy.zeros(1, dtype=mrc.header_image_dtype)
    assert(mrc.is_format_header(ar))
    ar = numpy.zeros(1, dtype=numpy.float)
    assert(not mrc.is_format_header(ar))

def test_is_readable():
    '''
    '''
    
    empty_image = numpy.zeros((78,200))
    eman_format.write_image(test_file, empty_image)
    assert(mrc.is_readable(test_file))
    os.unlink(test_file)

def test_read_header():
    '''
    '''
    
    test_is_readable()

def test_iter_images():
    '''
    '''
    
    empty_image = numpy.random.rand(78,200).astype('<f4')
    empty_image2 = numpy.random.rand(78,200).astype('<f4')
    mrc.write_image(test_file, empty_image, 0)
    mrc.write_image(test_file, empty_image2, 1)
    #eman_format.write_image(test_file, empty_image)#, 0)
    #eman_format.write_image(test_file, empty_image2, 1)
    for i, img in enumerate(mrc.iter_images(test_file)):
        ref = empty_image if i == 0 else empty_image2
        numpy.testing.assert_allclose(ref, img)
    os.unlink(test_file)
    
def test_read_image():
    '''
    '''
    
    numpy.random.seed(1)
    #empty_image = numpy.random.rand(78,200).astype('<f4')
    empty_image = numpy.random.rand(78,200).astype(numpy.float32)
    mrc.write_image(test_file, empty_image)
    #eman_format.write_image(test_file, empty_image)
    
    numpy.testing.assert_allclose(empty_image, eman_format.read_image(test_file))
    numpy.testing.assert_allclose(empty_image, mrc.read_image(test_file))
    os.unlink(test_file)
    
def test_read_image64():
    '''
    '''
    
    numpy.random.seed(1)
    empty_image = numpy.random.rand(78,200).astype(numpy.float64)
    #eman_format.write_image(test_file, empty_image)
    mrc.write_image(test_file, empty_image)
    numpy.testing.assert_allclose(empty_image, mrc.read_image(test_file))
    os.unlink(test_file)
    
def test_write_image():
    '''
    '''
    
    numpy.random.seed(1)
    empty_image = numpy.random.rand(78,200)
    mrc.write_image(test_file, empty_image)
    numpy.testing.assert_allclose(empty_image, eman_format.read_image(test_file))
    os.unlink(test_file)


