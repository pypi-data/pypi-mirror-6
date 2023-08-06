.. _scripts:

*******
Scripts
*******

phsh.py
=======

Command line usage
------------------

The *phsh.py* script is placed into the system ``PATH`` during installation of the 
phaseshifts package. It can then be used from the command line, e.g. ``phsh.py --help`` 
will produce a list of command line options::

  usage: phsh.py [-h] -b <bulk_file> -i <slab_file> [-t <temp_dir>] [-l <lmax>]
               [-f <format>] [-S <subdir>] [-v] [-V]


  phsh - quickly generate phase shifts

        Created by Liam Deacon on 2013-11-15.
        Copyright 2013-2014 Liam Deacon. All rights reserved.

        Licensed under the MIT license (see LICENSE file for details)

        Please send your feedback, including bugs notifications
        and fixes, to: liam.deacon@diamond.ac.uk

      usage:-

    optional arguments:
    -h, --help            show this help message and exit
    -b <bulk_file>, --bulk <bulk_file>
                          path to MTZ bulk or CLEED *.bul input file
    -i <slab_file>, --slab <slab_file>
                          path to MTZ slab or CLEED *.inp input file
    -t <temp_dir>, --tmpdir <temp_dir>
                          temporary directory for intermediate file generation
    -l <lmax>, --lmax <lmax>
                          Maximum angular momentum quantum number (default=10)
    -f <format>, --format <format>
                          Use specific phase shift format i.e. 'CLEED'
                          (default=None)
    -S <subdir>, --store <subdir>
                          Keep intermediate files in subdir when done
    -v, --verbose         set verbosity level [default: None]
    -V, --version         show program's version number and exit

CLEED compatibility
-------------------
It is possible to use this script to generate phase shift files iteratively 
during a geometry search for the CLEED package. In this manner phase shifts 
will be generated at the beginning of each cycle of the search.

For this to work, the environment variable ``CSEARCH_LEED`` must point to the 
`phsh.py` script, which will invoke the LEED program in ``PHASESHIFT_LEED`` 
after execution. When operating in this mode, the following assumptions are made:

 1. `-b <bulk_file>` option not needed and the filename is assumed by 
    cd ..changing the file extension of `<slab_file>` to '.bul'
 2. `-f CLEED` format is implied.
 3. The generated phase shifts are stored in the directory set by the `CLEED_PHASE` 
    environment variable.
 4. `<lmax>` is equal to 10, unless additional parameter syntax is given in the CLEED 
    `\*.inp` file.
  
A full list of additional syntax to customise the generation of the phase shifts 
when using CLEED input files can be found in the phaseshifts.leed documentation.

.. note::
  If the ``PHASESHIFT_LEED`` environment variable is not found, but ``CLEED_PHASE``
  is, however, found then the program will place the generated files in this 
  directory unless a specific `-S <subdir>` is provided.
