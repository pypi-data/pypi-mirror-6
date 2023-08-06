VERSION="0.1.1"

def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration

    config = Configuration(None, parent_package, top_path)
    config.set_options(ignore_setup_xxx_py=True,
                       assume_default_configuration=True,
                       delegate_options_to_subpackages=True,
                       quiet=True)
    
    config.add_subpackage('forthrast','forthrast')

    return config

def setup_package():

    from numpy.distutils.core import setup

    setup(
        name = "forthrast",
        version = VERSION,
        description = "A simple timeline interpolator for images",
        classifiers = [ "Development Status :: 2 - Pre-Alpha",
                        "Environment :: Console",
                        "Intended Audience :: Science/Research",
                        "License :: OSI Approved :: BSD License",
                        "Operating System :: MacOS :: MacOS X",
                        "Operating System :: POSIX :: Linux",
                        "Programming Language :: Python", ],
        keywords='image interpolation timeline',
        author="Matthew J. Turk",
        author_email="matthewturk@gmail.com",
        url = "http://bitbucket.org/MatthewTurk/forthrast",
        license="BSD",
        configuration=configuration,
    )
    return

if __name__ == '__main__':
    setup_package()
