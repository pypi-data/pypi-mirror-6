===================
PHASESHIFTS PACKAGE
===================

This package is a Python-based implementation of the  Barbieri/Van Hove 
phase shift (*phsh*) calculation package needed to produce phase shifts for 
various LEED packages (including CLEED), as well as for certain XPD packages. 
To quote the original authors site: 

"The phase shift calculation is performed in several steps:

1. Calculation of the radial charge density for a free atom.

2. Calculation of the radial muffin-tin potential for atoms embedded in a 
   surface defined by the user (the surface is represented by a slab that 
   is periodically repeated in 3 dimensions, within vacuum between the 
   repeated slabs); various approximations to the exchange potential 
   are available; relativistic effects are taken into account.

3. Calculation of phase shifts from the muffin-tin potential.

4. Elimination of pi-jumps in the energy dependence of the phase shifts."

.. note:: You can get the original Fortran source (& learn more about the *phsh* programs) from:

   http://www.icts.hkbu.edu.hk/surfstructinfo/SurfStrucInfo_files/leed/leedpack.html

Install
=======

The `phaseshifts` package requires CPython 2.6 or later and also uses the
`numpy`, `scipy` and `periodictable` packages. Unfortunately, it has only
been tested extensively with Python 2.7, so your milage may vary. To perform
a setup follow the steps below.

 1. Install the numpy, scipy and periodictable packages. 
    
    On systems with PyPI this can be done using the command:
	
    .. code:: bash
         
		pip install numpy scipy periodictable

    Or if you have the easy_install package:
    
    .. code:: bash
         
		 easy_install install numpy scipy periodictable

    Alternatively download and install these packages manually following the
    instructions provided for the respective packages.

 2. To install the phaseshifts package:

    .. code:: bash
         
		python setup.py install  

    With any luck the package has been installed successfully. A set of test scripts
    are provided, however a simple check may suffice using an interactive session of 
    the python interpreter:

      >>> import phaseshifts
      >>> from phaseshifts import libphsh  # compiled FORTRAN .pyd or .so using f2py

    If these execute without errors then it is likely that all is well, but in case of 
    problems or bugs please use the contact provided below and I will do my best to 
    address the problem quickly.
    
    .. note:: If you encounter problems when building under windows using the MSCV 
              compiler then try the following:
              
              .. code:: bash
                   
                 python setup.py config --compiler=mingw32 build --compiler=mingw32 install
              
              If you continue to experience problems you may need to install the appropriate
              MSVC for your installation (e.g. Visual C++ 2008 Express for Python 2.7).
            

.. tip:: On Windows systems it may be easier to install a scientific python distibution 
         rather than install the dependencies from source - I use Python(x,y) with mingw 
         (gcc & gfortran) installed, which can be found at:
		 
         http://code.google.com/p/pythonxy


About the code
==============

The example source codes provided in this package are intended to be 
instructional in calculating phase shifts. While it is not recommended to 
use the example code in production, the code
should be sufficient to explain the general use of the library.

If you aren't familiar with the phase shift calculation process, you can 
read further information in ``doc/`` folder:

+ ``phshift2007.rst`` - a brief user guide/documentation concerning the input files 
  (& details of the original fortran `phshift` package).
+ ``manual.pdf``      - a more detailed overview of the library functions and how to
  calculate phase shifts using the convenience functions in this package. This is not
  yet finished and so the reader is referred to the above document for the time being.

For those wanting a crash course I advise reading the phsh2007.txt document.
See the ``examples/`` directory to get an idea of the structure of the input files 
(for a random selection of models & elements). In particular see the ``cluster_Ni.i``
file for helpful comments regarding each line of input.

Those of you who are eager to generate phase shifts - first look at the example
cluster files for a bulk and slab calculation, noting that the atoms in the model
are in fractional (SPA) units of the unitcell. Next, after creating a bulk and 
slab model in the ``cluster.i`` format, simply use the following python code:
 
   >>> import phaseshifts as phsh
   >>> phsh.phaseshifts.gen_from_inputs(bulk='cluster_bulk.i', slab='cluster_slab.i')

This will hopefully produce the desired phase shift output files (at least for 
simple models) and works by assessing the two models to determine what output to
produce. For more detailed documentation and function use refer to the pdf manual.  

Acknowledgements
================

As with all scientific progress, we stand on the shoulders of giants. If this 
package is of use to you in publishing papers then please acknowledge the 
following people who have made this package a reality:

 - **A. Barbieri** and **M.A. Van Hove** - who developed most of the original 
   fortran code. Use *A. Barbieri and M.A. Van Hove, private communication.* 
   (see ``doc/phsh2007.txt`` for further details).
 
 - **E.L. Shirley** - who developed part of the fortran code during work towards his
   PhD thesis (refer to the thesis: *E.L. Shirley, "Quasiparticle calculations in 
   atoms and many-body core-valence partitioning", University of Illinois, Urbana, 1991*).

 - **Christoph Gohlke** - who developed the elements.py module used extensively throughout
   for the modelling convenience functions (see 'elements.py' for license details). 

 I would also be grateful if you acknowledge this python package (*phaseshifts*) as: 
 *L.M. Deacon, private communication.*


Thanks
------

I wish to personally add a heartfelt thanks to both Eric Shirley and Michel Van Hove 
who have kindly allowed the use of their code in the ``libphsh.f`` file needed for the
underlying low-level functions in this package. 

Contact
=======

This package is developed/maintained in my spare time so any bug reports, patches, 
or other feedback are very welcome and should be sent to: liam.m.deacon@gmail.com

The project is in the early developmental stages and so anyone who wishes to get 
involved are most welcome (simply contact me using the email above).

Todo
====

 1. Full implementation of python convenience functions and classes to easily 
    generate phase shift output files.

 2. Documentation - the manual has not yet been started and so is a high priority
    after No. 1. The current aim is to use sphinx to generate html and latex documents
    for semi-automated generation of both the tutorial and supporting website.  

 3. Test suit to verify the package is working as expected.

 4. GUI frontend (Qt ui files are provided in the ``gui/`` directory for anyone 
    wishing to undertake this challenge). Other frontends are welcome (I use Qt 
    due to familiarity/experience). For those wishing a sneak preview, try executing
    ``main.pyw``

See TODO.rst for more information.

Author list
===========

  - Liam Deacon - *current maintainer*