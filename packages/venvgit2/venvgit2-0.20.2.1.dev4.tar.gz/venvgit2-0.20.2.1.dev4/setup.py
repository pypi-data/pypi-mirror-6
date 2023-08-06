#!/usr/bin/env python
"""
    setup
    ~~~~~
"""

import os
import warnings
from glob import glob
from shutil import rmtree
from tempfile import mkdtemp
from setuptools import setup
from setuptools.command.install import install
from subprocess import check_call, CalledProcessError


class Dirs(object):
    """Get a scratch space for compiling and stuff"""

    def __init__(self):
        self.prefix = os.environ.get('VIRTUAL_ENV')
        if self.prefix is None:
            warnings.warn('this does not look like a virtualenv. trying with /usr/local')
            self.prefix = '/usr/local'
        self.src = os.getcwd()
        self.libgit2_src = os.path.join(self.src, 'libgit2')  # source
        self.pygit2_src = os.path.join(self.src, 'pygit2')  # source

    def __enter__(self):
        self.work_dir = mkdtemp()
        return self

    def __exit__(self, *args):
        os.chdir(self.src)
        rmtree(self.work_dir)


def cmake_is_installed():
    print('Looking for cmake...')
    try:
        check_call(['which', 'cmake'])
        return True
    except CalledProcessError:
        return False


def pythondev_is_installed():
    """ inspried by http://stackoverflow.com/questions/4848566/check-for-existence-of-python-dev-files-from-bash-script"""
    print('Looking for python dev files...')
    try:
        from distutils import sysconfig
    except ImportError as e:
        return False
    includepy = sysconfig.get_config_vars()['INCLUDEPY']
    pythonh = os.path.join(includepy, 'Python.h')
    dev_present = os.path.isfile(pythonh)
    return dev_present


def install_libgit2(dirs):
    """See https://github.com/libgit2/libgit2/blob/development/README.md"""
    os.chdir(dirs.work_dir)
    print('libgit2 cmake...')
    libgit2_cmd = ['cmake', dirs.libgit2_src, '-DBUILD_CLAR=OFF']
    libgit2_cmd.append('-DCMAKE_INSTALL_PREFIX={}'.format(dirs.prefix))
    check_call(libgit2_cmd)
    print('libgit2 building...')
    check_call(['cmake', '--build', dirs.work_dir, '--target', 'install'])


def install_pygit2(dirs):
    """See http://www.pygit2.org/install.html"""
    os.environ['LIBGIT2'] = dirs.prefix
    os.environ['LDFLAGS'] = "-Wl,-rpath='{}/lib',--enable-new-dtags {}" \
                            .format(dirs.prefix, os.environ.get('LDFLAGS', ''))
    script = os.path.join(dirs.pygit2_src, 'setup.py')
    os.chdir(dirs.pygit2_src)
    print('pygit2 clean...')
    check_call(['python', script, 'clean'])
    print('pygit2 build...')
    check_call(['python', script, 'build'])
    print('pygit2 install...')
    check_call(['python', script, 'install'])


class InstallEverything(install):
    """Install everything..."""
    def run(self):
        if not cmake_is_installed():
            warnings.warn("cmake does not appear to be installed...")
        if not pythondev_is_installed():
            warnings.warn("python development headers do not appear to be installed...")
        with Dirs() as dirs:
            install_libgit2(dirs)
            install_pygit2(dirs)
        install.run(self)


setup(
    name="venvgit2",
    description="Install libgit2 and pygit2 in a virtualenv",
    long_description=open('README.rst').read(),
    version="0.20.2.1.dev4",
    cmdclass={
      'install': InstallEverything,
    },
    author='uniphil',
    author_email='uniphil@gmail.com',
    license='Public Domain',
    url='http://github.com/uniphil/venvgit2',
)
