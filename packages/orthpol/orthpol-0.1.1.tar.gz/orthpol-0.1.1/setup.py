#
# This file is part of SpectralToolbox.
#
# SpectralToolbox is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SpectralToolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with SpectralToolbox.  If not, see <http://www.gnu.org/licenses/>.
#
# DTU UQ Library
# Copyright (C) 2014 The Technical University of Denmark
# Scientific Computing Section
# Department of Applied Mathematics and Computer Science
#
# Author: Daniele Bigoni
#

from numpy.distutils.core import setup, Extension
from numpy.distutils.command.install import install
import os, sys

class orthpolxx_install(install):
    
    def run(self):

        print "Installation of ORTHPOLxx"
        
        virtenv_dir = os.environ.get('VIRTUAL_ENV')
        
        os.chdir("./ORTHPOLxx")

        error = os.system("chmod u+x configure")
        if error: raise Exception("Compile error of ORTHPOLxx")
        
        if virtenv_dir == None:
            error = os.system("./configure")
        else:
            error = os.system("./configure --prefix=" + virtenv_dir)

        if error: raise Exception("Compile error of ORTHPOLxx")
        error = os.system("make")
        if error: raise Exception("Compile error of ORTHPOLxx")
        error = os.system("make install")
        if error: raise Exception("Compile error of ORTHPOLxx")
        
        error = os.system("make clean")
        if error: raise Exception("Compile error of ORTHPOLxx")
        
        os.chdir("../")
        
        print "Installation of PyORTHPOL"
        
        install.run(self)


if __name__ == "__main__":
    
    virtenv_dir = os.environ.get('VIRTUAL_ENV')
    if virtenv_dir == None:
        oxx_cflags = '`pkg-config --cflags liborthpol-1.0`'
        oxx_ld = '`pkg-config --libs liborthpol-1.0`'
    else:
        oxx_cflags = '`pkg-config --cflags ' + virtenv_dir + '/lib/pkgconfig/liborthpol-1.0.pc`'
        oxx_ld = '`pkg-config --libs ' + virtenv_dir + '/lib/pkgconfig/liborthpol-1.0.pc`'
    
    ext_modules = [ Extension('orthpol', 
                              ['src/PyORTHPOL.cpp'],
                              extra_compile_args = ['-lgfortran', '-g', '-O0', oxx_cflags],
                              extra_link_args = ['-lgfortran', '-g', '-O0', oxx_ld])
                    ]
    setup(
        name='orthpol',
        version = "0.1.1",
        license = "COPYING.LESSER",
        description = "Python wrapper for the ORTHPOL package",
        url="http://www2.compute.dtu.dk/~dabi/index.php?slab=dtu-uq",
        author = "Daniele Bigoni",
        author_email = "dabi@dtu.dk",
        ext_modules = ext_modules,
        cmdclass={'install': orthpolxx_install})
        # configuration=configuration)

