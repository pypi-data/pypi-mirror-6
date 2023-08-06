''' Reconstruct a 3D volume from a set of windowed projection images



.. Created on Feb 28, 2013
.. codeauthor:: Robert Langlois <rl2528@columbia.edu>
'''
from ..core.app import program
from ..core.image import ndimage_file
from ..core.image import preprocess_utility
from ..core.metadata import format_alignment
from ..core.metadata import spider_params
from ..core.metadata import format_utility
from ..core.image import reconstruct
from ..core.parallel import mpi_utility
from ..core.parallel import openmp
import numpy
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

def batch(files, image_file, output, rand_subset=0, experimental=False, experimental_2d=False, **extra):#, neig=1, nstd=1.5
    '''Concatenate files and write to a single output file
        
    :Args
    
        input_vals : list 
                     Tuple(view id, image labels and alignment parameters)
        output : str
                 Filename for output file
        extra : dict
                Unused key word arguments
                
    Returns:
    
        filename : str
                   Current filename
    '''
    
    if experimental: _logger.info("Experimental shared memory: enabled")
    if experimental_2d: _logger.info("Experimental 2D aligned images: enabled")
    if image_file: _logger.info("Using image file: %s"%image_file)
    if rand_subset: _logger.info("Drawing random subset: %d"%rand_subset)
    if extra['scale_spi']: _logger.info("Scaling translations for pySPIDER")
    if extra['thread_count']: _logger.info("Using %d threads"%extra['thread_count'])
    
    openmp.set_thread_count(1)
    align, image_size = None, None
    ctf_param=None
    if mpi_utility.is_root(**extra): 
        files, align, ctf_param = format_alignment.read_alignment(files[0], image_file, use_3d=not experimental_2d, ctf_params=True, **extra)
        filename = files[0] if isinstance(files, tuple) else files[0][0]
        image_size = ndimage_file.read_image(filename).shape[0]
        _logger.info("Reconstructing %d projections"%len(align))
    else: files=None
    files = mpi_utility.broadcast(files, **extra)
    align = mpi_utility.broadcast(align, **extra)
    ctf_param = mpi_utility.broadcast(ctf_param, **extra)
    image_size = mpi_utility.broadcast(image_size, **extra)
    extra.update(ctf_param)
    
    selection = numpy.arange(len(align), dtype=numpy.int)
    if rand_subset > 0:
        selection = numpy.random.choice(selection, rand_subset, False)
    curr_slice = mpi_utility.mpi_slice(len(align), **extra)
    even = numpy.arange(0, len(selection[curr_slice]), 2, dtype=numpy.int)
    odd = numpy.arange(1, len(selection[curr_slice]), 2, dtype=numpy.int)
    if isinstance(files, tuple):
        _logger.debug("Supports stacks with SPIDER filenames")
        image_file, label = files
        label = label[selection].copy()
        align = align[selection].copy()
        
        idx = numpy.argsort(label[:, 0]).squeeze()
        label = label[idx].copy()
        align = align[idx].copy()
        iter_single_images1 = ndimage_file.iter_images(image_file, label[even])
        iter_single_images2 = ndimage_file.iter_images(image_file, label[odd])
        # todo support multiple spider prefixes
    else:
        _logger.debug("Supports stacks non-SPIDER filenames")
        if len(selection) != len(files):
            files = [files[i] for i in selection]
            align = align[selection].copy()
        
        iter_single_images1 = ndimage_file.iter_images([files[i] for i in even])
        iter_single_images2 = ndimage_file.iter_images([files[i] for i in odd])
    align_curr = align[curr_slice].copy()
    align1 = align_curr[even]
    align2 = align_curr[odd]
    if experimental_2d:
        vol = reconstruct.reconstruct3_bp3f_mp(image_size, iter_single_images1, iter_single_images2, align1, align2, process_image=preprocess_utility.phaseflip_align2d, shared=experimental, **extra)
    else:
        vol = reconstruct.reconstruct3_bp3f_mp(image_size, iter_single_images1, iter_single_images2, align1, align2, process_image=preprocess_utility.phaseflip_shift, shared=experimental, **extra)
    if vol is not None: 
        ndimage_file.write_image(output, vol[0].T.copy())
        ndimage_file.write_image(format_utility.add_prefix(output, 'h1_'), vol[1].T.copy())
        ndimage_file.write_image(format_utility.add_prefix(output, 'h2_'), vol[2].T.copy())
    _logger.info("Complete")

def setup_options(parser, pgroup=None, main_option=False):
    # Collection of options necessary to use functions in this script
    
    from ..core.app.settings import OptionGroup
    group = OptionGroup(parser, "Reconstruct", "Reconstruct a volume from an alignment file and particle stacks",  id=__name__)
    group.add_option("",     scale_spi=False,           help="Scale the SPIDER translation (if refinement was done by pySPIDER)")
    group.add_option("",     apix=0.0,                  help="Pixel size for the data")
    group.add_option("-t",   thread_count=1,            help="Number of processes per machine", gui=dict(minimum=0), dependent=False)
    group.add_option("-r",   rand_subset=0,             help="Reconstruct a random subset of the given size", gui=dict(minimum=0), dependent=False)
    group.add_option("",     experimental=False,        help="Test experimental shared memory")
    group.add_option("",     experimental_2d=False,     help="Test 2d representation of alignment")
    group.add_option("",     class_index=0,             help="Select a specifc class within the alignment file")
    pgroup.add_option_group(group)
    if main_option:
        pgroup.add_option("-i", input_files=[], help="List of alignment files, e.g. data.star", required_file=True, gui=dict(filetype="open"))
        pgroup.add_option("-m", image_file="",  help="Image template for SPIDER alignment files, e.g. cluster/win/win_00000.dat ", required_file=False, gui=dict(filetype="open"))
        pgroup.add_option("-o", output="",      help="Output filename for the volume, e.g. raw_vol.dat", gui=dict(filetype="save"), required_file=True)
        spider_params.setup_options(parser, pgroup, False)

def check_options(options, main_option=False):
    #Check if the option values are valid
    from ..core.app.settings import OptionValueError
    
    if len(options.input_files) > 0 and not format_alignment.is_relion_star(options.input_files[0]):
        if options.image_file == "": raise OptionValueError, "SPIDER alignment files require the --image-file (-m) option to be set!"
        if options.param_file == "": raise OptionValueError, "SPIDER alignment files require the --param-file (-p) option to be set!"
    else:
        if options.apix == 0.0: raise OptionValueError, "Relion alignment files require the --apix option to be set!"

def main():
    #Main entry point for this script
    program.run_hybrid_program(__name__,
        description = '''Reconstruct a volume from a set of projections
                        
                        Example:
                         
                         # SPIDER Alignment file
                        $ %prog alignment_file.dat --image-file win_0000.dat -p params.dat -o vol.dat
                        
                        # Relion Star file
                        $ %prog alignment_file.star -o vol.dat
                        
                      ''',
        use_version = True,
        supports_OMP=False,
        supports_MPI=True,
    )

if __name__ == "__main__": main()

