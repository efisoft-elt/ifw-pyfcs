"""
@brief temp release of pyfcs client for sharing purposes  
"""

import os

from wtools.project import declare_project, default_build

declare_project('ifw-pyfcs', '0.1.0',
                requires='cxx python nosetests cii',
                recurse='pyfcs', 
		cxx_std='c++17'
		)

