from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging
import optparse

from lib2to3.main import warn, StdoutRefactoringTool
from lib2to3 import refactor

from libmodernize.fixes import lib2to3_fix_names
from libmodernize import __version__


def main(args=None):
    """Main program.

    Returns a suggested exit status (0, 1, 2).

    """
    # Set up option parser
    parser = optparse.OptionParser(usage='modernize [options] file|dir ...',
                                   version='%prog {0}'.format(__version__))
    parser.add_option('-d', '--doctests', action='store_true',
                      help='fix up doctests')
    parser.add_option('-f', '--fix', action='append', default=[],
                      help='each FIX specifies a transformation; default: all')
    parser.add_option('-j', '--processes', action='store', default=1,
                      type='int', help='Run 2to3 concurrently')
    parser.add_option('-x', '--nofix', action='append', default=[],
                      help='prevent a fixer from being run.')
    parser.add_option('-l', '--list-fixes', action='store_true',
                      help='list available transformations')
    parser.add_option('-p', '--print-function', action='store_true',
                      help='modify the grammar so that print() is a function')
    parser.add_option('-v', '--verbose', action='store_true',
                      help='more verbose logging')
    parser.add_option('--no-diffs', action='store_true',
                      help="don't show diffs of the refactoring")
    parser.add_option('-w', '--write', action='store_true',
                      help='write back modified files')
    parser.add_option('-n', '--nobackups', action='store_true', default=False,
                      help="don't write backups for modified files.")
    parser.add_option('--future-unicode', action='store_true', default=False,
                      help='use unicode_strings __future__ feature '
                           '(only useful for Python 2.6+).')

    fixer_pkg = 'libmodernize.fixes'
    avail_fixes = set(refactor.get_fixers_from_package(fixer_pkg))
    avail_fixes.update(lib2to3_fix_names)

    # Parse command line arguments
    refactor_stdin = False
    flags = {}
    options, args = parser.parse_args(args)

    if not args:
        parser.error('At least one file or directory argument required; '
                     'use --help to show usage')

    if not options.write and options.no_diffs:
        warn(
            "not writing files and not printing diffs; that's not very useful")

    if not options.write and options.nobackups:
        parser.error("Can't use -n without -w")

    if options.list_fixes:
        print('Available transformations for the -f/--fix option:')
        for fixname in sorted(avail_fixes):
            print(fixname)
        if not args:
            return 0

    if '-' in args:
        refactor_stdin = True
        if options.write:
            parser.error("Can't write to stdin")

    if options.print_function:
        flags['print_function'] = True

    # Set up logging handler
    level = logging.DEBUG if options.verbose else logging.INFO
    logging.basicConfig(format='%(name)s: %(message)s', level=level)

    # Initialize the refactoring tool
    unwanted_fixes = set(options.nofix)

    if not options.future_unicode:
        unwanted_fixes.add('libmodernize.fixes.fix_unicode_future')

    if options.doctests:
        unwanted_fixes.add('libmodernize.fixes.fix_print')
        unwanted_fixes.add('libmodernize.fixes.fix_absolute_import_future')
    else:
        # Use fix_absolute_import_future instead.
        unwanted_fixes.add('lib2to3.fixes.fix_import')

    explicit = set()
    if options.fix:
        all_present = False
        for fix in options.fix:
            if fix == 'all':
                all_present = True
            else:
                explicit.add(fix)
        requested = avail_fixes.union(explicit) if all_present else explicit
    else:
        requested = avail_fixes.union(explicit)
    fixer_names = requested.difference(unwanted_fixes)
    rt = StdoutRefactoringTool(sorted(fixer_names), flags, sorted(explicit),
                               options.nobackups, not options.no_diffs)

    # Refactor all files and directories passed as arguments
    if not rt.errors:
        if refactor_stdin:
            rt.refactor_stdin()
        else:
            try:
                rt.refactor(args, options.write, options.doctests,
                            options.processes)
            except refactor.MultiprocessingUnsupported:
                assert options.processes > 1
                parser.error("Sorry, -j isn't supported on this platform")
        rt.summarize()

    # Return error status (0 if rt.errors is zero)
    return int(bool(rt.errors))
