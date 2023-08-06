#! /usr/bin/env python2.4
# -*- coding: iso-8859-1 -*-

"""
Run a Python script under hotshot's control.

Adapted from a posting on python-dev by Walter Dörwald

usage %prog [ %prog args ] filename [ filename args ]

Any arguments after the filename are used as sys.argv for the filename.
"""

import sys
import optparse
import os
import hotshot
import hotshot.stats
import imp
import commons
import pstats

PROFILE = "hotshot.prof"
PROFILER = "hotshot"

def run_hotshot(filename, profile, args):
    """This avoids the problem in hotshotmain.py of being unable to
    handle the common idiom of:

    if __name__ == '__main__': sys.exit( main( sys.argv ) )
    """
    prof = hotshot.Profile(profile)
    basename = os.path.splitext( os.path.basename( filename ) )[ 0 ]
    dirname = os.path.dirname( filename )
    #if dirname == '': dirname = '.'
    sys.path.insert(0, dirname)
    sys.argv = [filename] + args

    mainfile, mainpath, maindesc = \
            imp.find_module( basename, [ dirname ] )
    @commons.with_resource( mainfile )
    def import_localconf( mainfile ):
        return imp.load_module( basename, mainfile, mainpath, maindesc )
    module = import_localconf()

    prof.runcall( module.main, [ dirname ] )
    prof.close()
    dump_hotshot( profile, True )

def dump_hotshot( profile, do_stderr = False ):
    stats = hotshot.stats.load( profile )
    stats.sort_stats("time", "calls")

    if do_stderr:
        # print_stats uses unadorned print statements, so the only way
        # to force output to stderr is to reassign sys.stdout temporarily
        orig_stdout = sys.stdout
        sys.stdout = sys.stderr
        stats.print_stats()
        sys.stdout = orig_stdout
    else:
        stats.print_stats()

def dump_profile( profile, do_stderr = False ):
    stats = pstats.Stats( profile )
    stats.sort_stats("time", "calls")

    if do_stderr:
        # print_stats uses unadorned print statements, so the only way
        # to force output to stderr is to reassign sys.stdout temporarily
        orig_stdout = sys.stdout
        sys.stdout = sys.stderr
        stats.print_stats()
        sys.stdout = orig_stdout
    else:
        stats.print_stats()

def main(args):
    parser = optparse.OptionParser(__doc__)
    parser.disable_interspersed_args()
    parser.add_option("-P", "--profiler", action="store", default=PROFILER,
                      dest="profiler", help='Specify profiler to use')
    parser.add_option("-p", "--profile", action="store", default=PROFILE,
                      dest="profile", help='Specify profile file to use')
    parser.add_option("-d", "--dump", action="store_true",
                      dest="do_dump",
                      help='Dump the given stat profile as text')
    (options, args) = parser.parse_args(args)

    if len(args) == 0:
        if options.do_dump:
            parser.print_help("missing script to execute")
            return 1
        else:
            parser.print_help('missing stat profile to dump')
            return 1
    if options.profiler not in [ 'hotshot', 'profile' ]:
        parser.print_help( 'profiler must be "hotshot" or "profile"' )
        return 1

    filename = args[0]
    if options.profiler == 'hotshot':
        if options.do_dump:
            dump_hotshot(filename)
        else:
            run_hotshot(filename, options.profile, args[1:])
    elif options.profiler == 'profile':
        if options.do_dump:
            dump_profile(filename)
        else:
            pass # TODO this would just be replicated the profile.py
            #run_profile(filename, options.profile, args[1:])
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
