import sys
import os
import pathlib
from setuptools import setup
from io import open as io_open

package_name = 'cad_to_shapely'

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')


if sys.version_info[0] < 3 or sys.version_info[0] == 3 and sys.version_info[1] < 6:
    sys.exit('Sorry, Python < 3.6 is not supported')


setup(
    name=package_name,
    version='0.1a',
    packages = [package_name],
    description='Import CAD files to Shapely geometry',
    author='Jon Robinson',
    author_email='jonrobinson1980@gmail.com',
    long_description=long_description,
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Python',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering',
    ],
    url='https://github.com/aegis1980/cad_to_shapely',
    install_requires=['ezdxf', 'numpy', 'shapely' , 'geomdl', 'matplotlib'],
    extras_require={  # Optional
        'dev': ['matplotlib']
    },
    include_package_data=True,

)