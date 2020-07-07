import sys
import os
import pathlib
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='cad_to_shapely',
    version='0.1.1a',
    description='Import CAD files to Shapely geometry',
    author='Jon Robinson',
    author_email='jonrobinson1980@gmail.com',
    long_description=long_description,
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering',
    ],
    package_dir={'': 'src'}, 
    packages=find_packages(where='src'),  
    python_requires='>=3.6, <4',
    url='https://github.com/aegis1980/cad_to_shapely',
    install_requires=['ezdxf', 'numpy', 'shapely' , 'geomdl'],
    extras_require={  # Optional
        'dev': ['matplotlib']
    },
    include_package_data=True,
)
