# -*- coding: utf-8 -*-
#
#
# TheVirtualBrain-Framework Package. This package holds all Data Management, and
# Web-UI helpful to run brain-simulations. To use it, you also need do download
# TheVirtualBrain-Scientific Package (for simulators). See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details. You should have received a copy of the GNU General
# Public License along with this program; if not, you can download it here
# http://www.gnu.org/licenses/old-licenses/gpl-2.0
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (in press)
#
#

"""
This module the building of a cython wrapper around a C++ library for 
calculating the geodesic distance between points on a mesh surface.

To build::
  python setup.py build_ext --inplace

.. moduleauthor:: Gaurav Malhotra <Gaurav@tvb.invalid>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import numpy

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

geodesic_module = [Extension(name="gdist",          # Name of extension
                             sources=["gdist.pyx"], # Filename of Cython source
                             language="c++")]       # Cython create C++ source

include_directories = [numpy.get_include(), # NumPy dtypes
                       "geodesic_library"]  # geodesic distance, C++ library.

setup(ext_modules = geodesic_module, 
      include_dirs = include_directories, 
      cmdclass = {'build_ext': build_ext},
      name='gdist',
      license='GPL 2',
      version='1.0.3',
      url='https://github.com/the-virtual-brain/external_geodesic_library',
      maintainer='Marmaduke Woodman',
      maintainer_email='mmwoodman@gmail.com',
      install_requires=['numpy', 'scipy', 'cython'],
      description="Compute geodesic distances",
      long_description="""
The gdist module is a Cython interface to a C++ library 
(http://code.google.com/p/geodesic/) for computing
geodesic distance which is the length of shortest line between two 
vertices on a triangulated mesh in three dimensions, such that the line
lies on the surface. 

The algorithm is due Mitchell, Mount and Papadimitriou, 1987; the implementation
is due to Danil Kirsanov and the Cython interface to Gaurav Malhotra and 
Stuart Knock. 
"""
)
