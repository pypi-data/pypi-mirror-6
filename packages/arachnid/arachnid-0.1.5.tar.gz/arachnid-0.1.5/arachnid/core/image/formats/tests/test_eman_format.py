''' Unit testing for the image formats

.. Created on Aug 31, 2012
.. codeauthor:: Robert Langlois <rl2528@columbia.edu>
'''

from .. import eman_format
import numpy, os

test_file = 'test.mrc'

"""
def test_is_format_header():
    '''
    '''
    
    ar = numpy.zeros(1, dtype=eman_format.header_stack_dtype)
    assert(eman_format.is_format_header(ar))
    ar = numpy.zeros(1, dtype=eman_format.header_image_dtype)
    assert(eman_format.is_format_header(ar))
    ar = numpy.zeros(1, dtype=numpy.float)
    assert(not eman_format.is_format_header(ar))
"""

def test_is_readable():
    '''
    '''
    
    empty_image = numpy.zeros((78,78))
    eman_format.write_image(test_file, empty_image)
    assert(eman_format.is_readable(test_file))
    os.unlink(test_file)

def test_read_header():
    '''
    '''
    
    test_is_readable()

def test_iter_images():
    '''
    '''
    
    empty_image = numpy.zeros((78,78))
    empty_image2 = numpy.ones((78,78))
    eman_format.write_image(test_file, empty_image)#, 0)
    #eman_format.write_image(test_file, empty_image2, 1)
    for i, img in enumerate(eman_format.iter_images(test_file)):
        ref = empty_image if i == 0 else empty_image2
        numpy.testing.assert_allclose(ref, img)
    os.unlink(test_file)
    
def test_read_image():
    '''
    '''
    
    empty_image = numpy.zeros((78,78))
    eman_format.write_image(test_file, empty_image)
    numpy.testing.assert_allclose(empty_image, eman_format.read_image(test_file))
    os.unlink(test_file)
    
def test_write_image():
    '''
    '''
    
    empty_image = numpy.zeros((78,78))
    eman_format.write_image(test_file, empty_image)
    numpy.testing.assert_allclose(empty_image, eman_format.read_image(test_file))
    os.unlink(test_file)


