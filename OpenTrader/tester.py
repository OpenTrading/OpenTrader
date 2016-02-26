# -*-mode: python; py-indent-offset: 4; encoding: utf-8-dos; coding: utf-8 -*-

"""The test command lets us run the tests. By making running the tests from
the code, we can test the program in its final state (acceptance testing).
"""

"""
Tag selection on the command-line may be combined:
--tags=wip,slow
    This will select all the cases tagged either "wip" or "slow".
--tags=wip --tags=slow
    This will select all the cases tagged both "wip" and "slow".
"""

import sys
import os

from optparse import make_option

from doer import Doer

SDOC = __doc__
LOPTIONS = [make_option('--dir', action="store",
                        dest="sdir",
                        default=os.getcwd(),
                        help="directory the feature files will be read from. The directory must exist.")]

LCOMMANDS=[]

# --stop is required if you are also going to use --pdb
# --no-color is a good idea under Windwoes, unless you have an ANSI
# terminal eemulatore that works.
BEHAVE_ARGS="--stop --no-capture --no-capture-stderr --no-skipped --no-color"


class DoTest(Doer):
    __doc__ = SDOC
    # putting this as a module variable test it available
    # before an instance has been instantiated.
    global LCOMMANDS

    dhelp = {'': __doc__}

    def __init__(self, ocmd2):
        Doer.__init__(self, ocmd2, 'test')

    LCOMMANDS += ['features']
    def test_features(self):
        """test features will run the feature files tests.

test features uses the --dir option to the test command to know what
directory the feature files will be found in. The directory must exist,
and contain the subdirectory features/live_read.
"""
        
        from behave.__main__ import main as behave_main

        sdir = self.ovalues.sdir
        assert os.path.isdir(sdir), \
          "Directory does not exist: " +sdir
        sdir_live_read = os.path.join(sdir, 'features')
        assert os.path.isdir(sdir_live_read), \
          "Directory should contain features: " +sdir
        os.chdir(sdir)

        largs = BEHAVE_ARGS.split()
        # we exclude the tests tagged @wip Work in progress
        largs.extend(['--tags', '~wip', 'features'])
        iretval = behave_main(largs)

        assert iretval == 0, "ERROR: Behave tests failed"
        self.poutput("INFO: features passed in " + sdir)


    # maybe remove this as it duplicates load
    LCOMMANDS += ['load']
    def test_load(self):
        """test load will run an example script file.
It can run the scripts in the test/examples directory,
which are used to test the application.

test load uses the --dir option to the test command to know what
directory the files will be found in. The directory must exist.
"""
        self.poutput("INFO: use the load command directly, not test load")


        
    def bexecute(self, largs, ovalues):
        """bexecute executes the test command.

The testing feature files are run by the behave test-runner.
For full documentation on behave, see http://pythonhosted.org/behave/
"""
        self.largs = largs
        self.ovalues = ovalues

        self.vassert_args(largs, LCOMMANDS, imin=1)
        if self.bis_help(largs):
            return

        sdo = largs[0]
        if sdo == 'features':
            self.test_features()
            return

        return True


