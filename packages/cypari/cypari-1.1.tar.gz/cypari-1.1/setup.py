description = """\
CyPari is a Python wrapper for the `PARI library <http://pari.math.u-bordeaux.fr/>`_,
a computer algebra system for number theory computations.  It is derived from the
`corresponding component <http://www.sagemath.org/doc/reference/libs/sage/libs/pari/gen.html>`_
of `Sage <http://www.sagemath.org>`_ but is independent of the rest of Sage and
can be used with any recent version of Python.  
"""

import os, sys
from setuptools import setup, Command
from distutils.extension import Extension

try:
    from Cython.Distutils import build_ext
except ImportError:
    print('ERROR: Cython not installed, will not be able to install CyPari.')
    print('ERROR: Please install the Cython package into Python and try again.')
    sys.exit()

pari_ver = 'pari-2.5.5'
pari_include_dir = os.path.join(pari_ver, 'include')
pari_library_dir = os.path.join(pari_ver, 'lib')
pari_library = os.path.join(pari_library_dir, 'libpari.a')

if not os.path.exists(pari_library) and 'clean' not in sys.argv:
    if sys.platform == 'win32':
        print('Please run the bash script build_pari.sh first')
        sys.exit()
    if os.system('bash build_pari.sh') != 0:
        sys.exit("***Failed to build PARI library***")
    
class clean(Command):
    user_options = []
    def initialize_options(self):
        pass 
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -rf build dist')
        os.system('rm -rf cypari*.egg-info')
        os.system('rm -f cypari/gen.c cypari/gen.h cypari/*.pyc')

pari_gen = Extension('cypari.gen',
                     sources=['cypari/gen.pyx'],
                     include_dirs=[pari_include_dir],
                     library_dirs=[pari_library_dir],
                     libraries=['pari', 'm'],
                     )

setup(
  name = 'cypari',
  version = '1.1',
  author = 'William Stein, Marc Culler, and others',
  author_email = 'culler@math.uic.edu',
  maintainer = 'Marc Culler and Nathan Dunfield',
  maintainer_email = 'culler@math.uic.edu, nmd@illinois.edu',
  url = 'http://www.math.uic.edu/t3m',
  description = "Sage's PARI extension, modified to stand alone.",  
  long_description = description,
  license = 'GPL v2+',
  classifiers = [
      'Development Status :: 5 - Production/Stable',
      'Intended Audience :: Science/Research',
      'Topic :: Scientific/Engineering :: Mathematics',
      'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)'
      ], 
  platforms = ['Linux', 'OS X', 'Windows'],
  install_requires = ['cython'],
  packages = ['cypari'],
  cmdclass = {'build_ext': build_ext, 'clean':clean},
  ext_modules = [pari_gen],
  keywords = 'Pari, Sage, SnapPy',
  zip_safe = False,
)
