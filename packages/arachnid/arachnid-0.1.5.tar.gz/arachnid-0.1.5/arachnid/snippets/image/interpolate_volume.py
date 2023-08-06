''' Interporate a volume

Download to edit and run: :download:`interpolate_volume.py <../../arachnid/snippets/image/interpolate_volume.py>`

To run:

.. sourcecode:: sh
    
    $ python interpolate_volume.py

.. literalinclude:: ../../arachnid/snippets/image/interpolate_volume.py
   :language: python
   :lines: 16-
   :linenos:
'''
import sys
from arachnid.core.image import ndimage_file
from arachnid.core.image import ndimage_interpolate

if __name__ == '__main__':

    # Parameters
    
    input_file = sys.argv[1]
    bin_factor = float(sys.argv[2])
    output_file = sys.argv[3]
    
    img=ndimage_file.read_image(input_file)
    img=ndimage_interpolate.interpolate_bilinear(img, bin_factor)
    ndimage_file.write_image(output_file, img)