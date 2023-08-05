import os
from distutils.core import setup

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name = "epipy",
    version = "0.0.1",
    author = "Caitlin Rivers",
    author_email = "caitlin.rivers@gmail.com",
    description = "Python tools for epidemiology.",
    url = 'http://github.com/cmrivers/epipy',
    download_url = 'https://github.com/cmrivers/epipy/tarball/0.0.1',
    install_requires = ['Numpy >= 1.6.2',
                        'Matplotlib >=1.2.0',
                        'Networkx >=1.6.0',
                        'Pandas >= 0.12.0',
                        'Scipy >= 0.13'],
    license = "MIT",
    keywords = "epidemiology",
    packages = ['epipy'],
    scripts = ['epipy/basics.py',
               'epipy/case_tree.py',
               'epipy/checkerboard.py',
               'epipy/data_generator.py',
                'epipy/epicurve.py',
                'epipy/analyses.py'],
    long_description='README.md',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 2.7",
        "Natural Language :: English",
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics'],
)
