#!/usr/bin/env python

# Installation script for diffpy.srreal

"""diffpy.srreal - calculators for PDF, bond valence sum, and other
quantities based on atom pair interaction.

Packages:   diffpy.srreal
"""

import os
import glob
from setuptools import setup, find_packages
from setuptools import Extension
from numpy.distutils.misc_util import get_numpy_include_dirs


# define extension arguments here
ext_kws = {
        'libraries' : ['diffpy'],
        'extra_compile_args' : [],
        'extra_link_args' : [],
        'include_dirs' : get_numpy_include_dirs(),
}


# Figure out which boost library to use. This doesn't appear to consult
# LD_LIBRARY_PATH.
def get_boost_libraries():
    """Check for installed boost_python shared library.

    Returns list of required boost_python shared libraries that are installed
    on the system. If required libraries are not found, an Exception will be
    thrown.
    """
    baselib = "boost_python"
    boostlibtags = ['', '-mt']
    from ctypes.util import find_library
    for tag in boostlibtags:
        lib = baselib + tag
        found = find_library(lib)
        if found: break

    # Raise Exception if we don't find anything
    if not found:
        raise Exception("Cannot find shared boost_library library")

    libs = [lib]
    return libs


def create_extensions():
    "Initialize Extension objects for the setup function."
    blibs = [n for n in get_boost_libraries()
            if not n in ext_kws['libraries']]
    ext_kws['libraries'] += blibs
    ext = Extension('diffpy.srreal.srreal_ext',
            glob.glob('srrealmodule/*.cpp'),
            **ext_kws)
    return [ext]


# versioncfgfile holds version data for git commit hash and date.
# It must reside in the same directory as version.py.
MYDIR = os.path.dirname(os.path.abspath(__file__))
versioncfgfile = os.path.join(MYDIR, 'diffpy/srreal/version.cfg')

def gitinfo():
    from subprocess import Popen, PIPE
    kw = dict(stdout=PIPE, cwd=MYDIR)
    proc = Popen(['git', 'describe', '--match=v[[:digit:]]*'], **kw)
    desc = proc.stdout.read()
    proc = Popen(['git', 'log', '-1', '--format=%H %at %ai'], **kw)
    glog = proc.stdout.read()
    rv = {}
    rv['version'] = '-'.join(desc.strip().split('-')[:2]).lstrip('v')
    rv['commit'], rv['timestamp'], rv['date'] = glog.strip().split(None, 2)
    return rv


def getversioncfg():
    from ConfigParser import SafeConfigParser
    cp = SafeConfigParser()
    cp.read(versioncfgfile)
    gitdir = os.path.join(MYDIR, '.git')
    if not os.path.isdir(gitdir):  return cp
    d = cp.defaults()
    g = gitinfo()
    if g['version'] != d.get('version') or g['commit'] != d.get('commit'):
        cp.set('DEFAULT', 'version', g['version'])
        cp.set('DEFAULT', 'commit', g['commit'])
        cp.set('DEFAULT', 'date', g['date'])
        cp.set('DEFAULT', 'timestamp', g['timestamp'])
        cp.write(open(versioncfgfile, 'w'))
    return cp

versiondata = getversioncfg()

# define distribution
setup_args = dict(
        name = "diffpy.srreal",
        version = versiondata.get('DEFAULT', 'version'),
        namespace_packages = ['diffpy'],
        packages = find_packages(),
        test_suite = 'diffpy.srreal.tests',
        include_package_data = True,
        ext_modules = [],
        install_requires = [
            'diffpy.Structure',
        ],
        zip_safe = False,

        author = "Simon J.L. Billinge group",
        author_email = "sb2896@columbia.edu",
        maintainer = "Pavol Juhas",
        maintainer_email = "pavol.juhas@gmail.com",
        description = ("calculators for PDF, bond valence sum, and other "
                       "quantities based on atom pair interaction."),
        license = 'BSD-style license',
        url = "https://github.com/diffpy/diffpy.srreal/",
        keywords = "PDF BVS atom overlap calculator real-space",
        classifiers = [
            # List of possible values at
            # http://pypi.python.org/pypi?:action=list_classifiers
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: POSIX',
            'Operating System :: Unix',
            'Programming Language :: C++',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Topic :: Scientific/Engineering :: Chemistry',
            'Topic :: Scientific/Engineering :: Physics',
            'Topic :: Software Development :: Libraries',
        ],
)

if __name__ == '__main__':
    setup_args['ext_modules'] = create_extensions()
    setup(**setup_args)

# End of file
