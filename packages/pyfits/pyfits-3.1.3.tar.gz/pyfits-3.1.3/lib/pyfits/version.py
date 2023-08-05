"""This is an automatically generated file created by stsci.distutils.hooks.version_setup_hook.
Do not modify this file by hand.
"""

__all__ = ['__version__', '__vdate__', '__svn_revision__', '__svn_full_info__',
           '__setup_datetime__']

import datetime

__version__ = '3.1.3.dev'
__vdate__ = 'unspecified'
__svn_revision__ = 'Unversioned directory'
__svn_full_info__ = 'unknown'
__setup_datetime__ = datetime.datetime(2013, 11, 26, 13, 13, 42, 632954)

# what version of stsci.distutils created this version.py
stsci_distutils_version = '0.3.6'

if '.dev' in __version__:
    def update_svn_info():
        """Update the SVN info if running out of an SVN working copy."""

        import os
        import string
        import subprocess

        global __svn_revision__
        global __svn_full_info__

        path = os.path.abspath(os.path.dirname(__file__))

        run_svnversion = True

        try:
            pipe = subprocess.Popen(['svn', 'info', path],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            if pipe.wait() == 0:
                lines = []
                for line in pipe.stdout.readlines():
                    line = line.decode('latin1').strip()
                    if not line:
                        continue
                    lines.append(line)

                if not lines:
                    __svn_full_info__ = ['unknown']
                else:
                    __svn_full_info__ = lines
            else:
                run_svnversion = False
        except OSError:
            run_svnversion = False

        if run_svnversion:
            # If updating the __svn_full_info__ succeeded then use its output
            # to find the base of the working copy and use svnversion to get
            # the svn revision.
            for line in __svn_full_info__:
                if line.startswith('Working Copy Root Path'):
                    path = line.split(':', 1)[1].strip()
                    break

            try:
                pipe = subprocess.Popen(['svnversion', path],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                if pipe.wait() == 0:
                    stdout = pipe.stdout.read().decode('latin1').strip()
                    if stdout and stdout[0] in string.digits:
                        __svn_revision__ = stdout
            except OSError:
                pass

        # Convert __svn_full_info__ back to a string
        if isinstance(__svn_full_info__, list):
            __svn_full_info__ = '\n'.join(__svn_full_info__)


    update_svn_info()
    del update_svn_info
