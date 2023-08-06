''' Setup for core modules
'''

def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('parallel', parent_package, top_path)
    config.set_options(quiet=True)
    config.add_subpackage('core')
    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
