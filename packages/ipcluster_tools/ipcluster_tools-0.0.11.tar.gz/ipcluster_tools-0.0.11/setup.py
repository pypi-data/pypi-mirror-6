"""
Configure the ipcluster_tools package.
"""

import versioneer
from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


versioneer.versionfile_source = 'ipcluster_tools/_version.py'
versioneer.versionfile_build = 'ipcluster_tools/_version.py'
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = 'ipcluster_tools-'


DESCR = """
A collection of tools to watch jobs on ipython clusters.
"""

DISTNAME            = 'ipcluster_tools'
DESCRIPTION         = 'IPython cluster tools'
LONG_DESCRIPTION    = DESCR
MAINTAINER          = 'Nathan Faggian'
MAINTAINER_EMAIL    = 'nathan.faggian@gmail.com'
URL                 = 'https://github.com/nfaggian/ipcluster_tools'
LICENSE             = 'MIT'
DOWNLOAD_URL        = ''

cmd_class = versioneer.get_cmdclass()
cmd_class['test'] = PyTest

if __name__ == "__main__":

    setup(
        name=DISTNAME,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        url=URL,
        license=LICENSE,
        download_url=DOWNLOAD_URL,
        version=versioneer.get_version(),
        cmdclass=cmd_class,
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.3",
            "License :: OSI Approved",
            "License :: OSI Approved :: BSD License",
            'Topic :: Scientific/Engineering',
            'Operating System :: POSIX',
            'Operating System :: Unix',
            'Operating System :: MacOS',
        ],
        packages=['ipcluster_tools'],
        package_data={},
        entry_points={'console_scripts': ['ipcluster_watcher = ipcluster_tools.watcher:gui_watcher']},
        tests_require=['ipython', 'pytest'],
        install_requires=['ipython','pytest'])
