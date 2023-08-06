import os

#from setuptools import setup, find_packages
#import fix_setuptools_chmod
try:
    from setuptools import find_packages
except ImportError:
    from distutils.core import find_packages

from numpy.distutils.core import Extension, setup

#import phaseshifts
import sys, os

if len(sys.argv) == 1:
    sys.argv.append('install')
	
dist = setup(
        name = 'phaseshifts',
		#packages=['phaseshifts', 'phaseshifts.gui', 'phaseshifts.lib', 'phaseshifts.contrib'],
        packages = find_packages(),
        version='0.1.1-dev',
        author='Liam Deacon',
        author_email='liam.m.deacon@gmail.com',
        license='MIT License',
        url='https://pypi.python.org/pypi/phaseshifts',
        description='Python-based version of the Barbieri/Van Hove phase shift calculation package for LEED/XPD modelling',
        long_description=open(os.path.join('phaseshifts','README.rst')).read() if os.path.exists(os.path.join('phaseshifts','README.rst')) else None,
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: Console',
			'Environment :: X11 Applications :: Qt',  # The end goal is to have Qt or other GUI frontend
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering :: Chemistry',
            'Topic :: Scientific/Engineering :: Physics',
            ],
        keywords='phaseshifts atomic scattering muffin-tin diffraction',
        #recursive-include phaseshifts *.py *.pyw
        include_package_data = True,
        package_data = {
			# If any package contains *.txt or *.rst files, include them:
			'' : ['*.txt', '*.rst', '*.pyw'],
			'lib' : ['lib/*.f', 'lib/*.c', 'lib/*.h'],
            'gui' : ['gui/*.ui', 'gui/*.bat'],
            'gui/res' : ['gui/res/*.*']
			},
        #data_files = periodictable.data_files(),
        install_requires = ['scipy', 'numpy', 'periodictable'],
		ext_modules=[Extension(name='phaseshifts.lib.libphsh', sources=[os.path.join('phaseshifts','lib','libphsh.f')])],
)

# End of file
