''' Reconstruct a volume from a subset of projections

Download to edit and run: :download:`reconstruct_stack.py <../../arachnid/snippets/reconstruction/reconstruct_stack.py>`

To run:

.. sourcecode:: sh
    
    $ python reconstruct_stack.py

.. literalinclude:: ../../arachnid/snippets/reconstruction/reconstruct_stack.py
   :language: python
   :lines: 16-
   :linenos:
'''
import sys
#sys.path.append('/home/robertl/tmp/arachnid-0.0.1/')

from arachnid.core.app import tracing
from arachnid.core.metadata import format, spider_params
from arachnid.core.image import ndimage_file, rotate
from arachnid.core.image.ctf import correct as ctf_correct
from arachnid.core.image import reconstruct
import logging

def process_image(img, data, **extra):
    '''
    '''
    
    img = rotate.rotate_image(img, data[5], data[6], data[7])
    ctfimg = ctf_correct.phase_flip_transfer_function(img.shape, data[17], **extra)
    img = ctf_correct.correct(img, ctfimg)
    return img

if __name__ == "__main__":
    
    tracing.configure_logging()

    image_file = sys.argv[1]   # phase_flip_dala_stack.spi
    align_file = sys.argv[2]   # align.spi
    param_file = sys.argv[3]
    output = sys.argv[4]       # raw_vol.spi
    bin_factor = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0        # raw_vol.spi
    thread_count = 32
    
    extra = spider_params.read(param_file)
    extra.update(spider_params.update_params(bin_factor, **extra))
    print "Loaded param file"
    extra.update(thread_count=thread_count)
    
    align,header = format.read_alignment(align_file, ndarray=True)
    logging.error("Reconstructing %d particles"%len(align))
    selection = align[:, 15:17]
    align[:, 6:8] /= extra['apix']
    iter_single_images = ndimage_file.iter_images(image_file, selection)
    image_size = ndimage_file.read_image(image_file).shape[0]
    vol = reconstruct.reconstruct_bp3f_mp(iter_single_images, image_size, align, process_image=process_image, **extra)
    if vol is not None: 
        ndimage_file.write_image(output, vol)