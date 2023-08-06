#!/usr/local/bin/python2.7
# encoding: utf-8
'''
phsh - quickly generate phase shifts

phsh provides convenience functions to create phase shifts files
suitable for input into LEED-IV programs such as SATLEED and CLEED.

It defines classes_and_methods

@author:     Liam Deacon

@copyright:  2013 Diamond Light Source Ltd. All rights reserved.

@license:    MIT License (see LICENSE file for details)

@contact:    liam.deacon@diamond.ac.uk
'''

import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from phaseshifts import *

__all__ = []
__version__ = 0.1
__date__ = '2013-11-15'
__updated__ = '2013-11-15'
__contact__ = 'liam.deacon@diamond.ac.uk'

DEBUG = 0
TESTRUN = 1
PROFILE = 0


class Wrapper(object):
    '''Wrapper class to easily generate phase shifts'''
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @staticmethod
    def autogen_from_input(bulk_file, slab_file, **kwargs):
        '''
        Description
        -----------
        Generate phase shifts from a slab/cluster input file.
        
        Parameters
        ----------
        slab_file : str
            Path to the cluster slab MTZ input file.
        bulk_file : str
            Path to the cluster bulk MTZ input file.
        tmp_dir : str
            Temporary directory for intermediate files.
            
        Returns
        -------
        output_files : list(str)
           A list of phase shift output filenames 
        '''
        dummycell = model.Unitcell(1, 2, [[1, 0, 0], [0, 1, 0], [0, 0, 1]])

        # Load bulk model and calculate MTZ
        bulk_mtz = model.MTZ_model(dummycell, atoms=[])
        bulk_mtz.load_from_file(bulk_file)
        
        # Load slab model and calculate MTZ
        slab_mtz = model.MTZ_model(dummycell, atoms=[])
        slab_mtz.load_from_file(slab_file)
        

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
        
    def __str__(self):
        return self.msg
    
    def __unicode__(self):
        return self.msg


def main(argv=None):
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, 
                                                     program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

      Created by Liam Deacon on %s.
      Copyright 2013 Liam Deacon. All rights reserved.

      Licensed under the MIT license (see LICENSE file for details)

      Please send your feedback, including bugs notifications
      and fixes, to: %s

    usage:-
    ''' % (program_shortdesc, str(__date__), __contact__)

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, 
                                formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-b', '--bulk', dest='bulk', metavar='<bulk_file>', 
                            help="path to MTZ bulk input file")
        parser.add_argument('-s', '--slab', dest='slab', metavar='<slab_file>', 
                            help="path to MTZ slab (cluster) input file")
        parser.add_argument('-t', '--tmpdir', dest='tmpdir', 
                            metavar='<temp_dir>', 
                            help="temporary directory for intermediate "
                            "file generation")
        parser.add_argument('-S', '--store', dest='store', metavar='<subdir>', 
                            help="Keep intermediate files in subdir when done")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count",
                            help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', 
                            version=program_version_message)

        # Process arguments
        args = parser.parse_args()

        verbose = args.verbose

        if verbose > 0:
            pass
        
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        sys.argv.append("-v")
        sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'wrapper_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
