import os, sys

from setuptools import setup, find_packages, dist
from setuptools.command.test import test as TestCommand
from distutils.core import Command
from distutils.core import setup

if sys.version_info.major < 3:
    print('Please install with python version 3')
    sys.exit(1)

# Use buildout's path for eggs
def get_egg_cache_dir(self):
    egg_cache_dir = os.path.join(os.curdir, 'var', 'eggs')
    if not os.path.exists(egg_cache_dir):
        os.mkdir(egg_cache_dir)
        windows_support.hide_file(egg_cache_dir)
        readme_txt_filename = os.path.join(egg_cache_dir, 'README.txt')
    return egg_cache_dir
dist.Distribution.get_egg_cache_dir = get_egg_cache_dir


class DistClean(Command):
    description = 'Clean the repository from all buildout stuff'
    user_options = []

    def initialize_options(self): pass
    def finalize_options(self): pass

    def run(self):
        import shutil, os
        from glob import glob
        path = os.path.split(__file__)[0]
        shutil.rmtree(os.path.join(path, 'var'), ignore_errors=True)
        shutil.rmtree(os.path.join(path, 'bin'), ignore_errors=True)
        shutil.rmtree(os.path.join(path, '.tox'), ignore_errors=True)
        for fname in glob('*.egg-info'):
            shutil.rmtree(os.path.join(path, fname), ignore_errors=True)
        shutil.rmtree(os.path.join(path, '.eggs'), ignore_errors=True)
        shutil.rmtree(os.path.join(path, 'build'), ignore_errors=True)
        shutil.rmtree(os.path.join(path, 'dist'), ignore_errors=True)
        shutil.rmtree(os.path.join(path, '.installed.cfg'), ignore_errors=True)
        print("Repository is now clean!")


class Version(Command):
    description = 'Bump version number'
    user_options = [
            ('major', 'M', 'Bump major part of version number'),
            ('minor', 'm', 'Bump minor part of version number'),
            ('patch', 'p', 'Bump patch part of version number')]
    path = os.path.join(os.path.dirname(__file__), 'VERSION')
    _info = None

    def finalize_options(self, *args, **kwarg): pass
    def initialize_options(self, *args, **kwarg):
        self.major = None
        self.minor = None
        self.patch = None

    def run(self):
        if self.major:
            self.info()[0] += 1
            self.info()[1] = 0
            self.info()[2] = 0
        if self.minor:
            self.info()[1] += 1
            self.info()[2] = 0
        if self.patch:
            self.info()[2] += 1
        with open(self.path, 'w') as f:
            f.write(self.info_str())

    @classmethod
    def info(cls):
        if not cls._info:
            try:
                cls._info = list(int(x) for x in open(cls.path, 'r').read().strip().split('.'))
            except ValueError:
                print('Version parts shall all be integers')
                sys.exit(1)
            if len(cls._info) != 3:
                print('Version number is not conform, there should be exactly three parts')
                sys.exit(1)
        return cls._info

    @classmethod
    def info_str(self):
        return '.'.join(map(str, self.info()))


class PyTest(TestCommand):
    user_options = [
            ('exitfirst', 'x', "exit instantly on first error or failed test."),
            ('last-failed', 'l', "rerun only the tests that failed at the last run"),
            ('verbose', 'v', "increase verbosity"),
            ('pdb', 'p', "run pdb upon failure"),
            ('pep8', '8', "perform some pep8 sanity checks on .py files"),
            ('flakes', 'f', "run flakes on .py files"),
            ('pytest-args=', 'a', "Extra arguments to pass into py.test"),
            ]
    default_options = [
        '--cov=calenvite', '--cov-report', 'term-missing',
        '--capture=sys', 'tests'
    ]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = set()
        self.exitfirst = False
        self.last_failed = False
        self.verbose = 0
        self.pdb = False
        self.pep8 = False
        self.flakes = False

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        if isinstance(self.pytest_args, str):
            self.pytest_args = set(self.pytest_args.split(' '))
        if self.exitfirst:   self.pytest_args.add('-x')
        if self.pdb:   self.pytest_args.add('--pdb')
        if self.last_failed: self.pytest_args.add('--last-failed')
        if self.pep8:        self.pytest_args.add('--pep8')
        if self.flakes:      self.pytest_args.add('--flakes')
        self.pytest_args = list(self.pytest_args)
        if self.verbose:
            for v in range(self.verbose):
                self.pytest_args.append('-v')
        errno = pytest.main(self.pytest_args + self.default_options)
        sys.exit(errno)


setup(name='pycalenvite',
      version=Version.info_str(),
      description='Calendar Invitation service',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          # 'Development Status :: 3 - Alpha',
          # 'Development Status :: 4 - Beta',
          # 'Development Status :: 5 - Production/Stable',
          # 'Development Status :: 6 - Mature',
          # 'Development Status :: 7 - Inactive',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Topic :: Software Development',
          'Topic :: Software Development :: Version Control',
          'Topic :: Utilities',
      ],
      keywords='git',
      url='https://github.com/guyzmo/pycalenvite',
      author='Bernard `Guyzmo` Pratz',
      author_email='guyzmo+calenvite@m0g.net',
      setup_requires=[
          'setuptools-markdown'
      ],
      long_description_markdown_filename='README.md',
      include_package_data = True,
      install_requires=[
            'docopt',
            'ics',
            'flask',
            'Flask-restful',
            'Flask-Webpack',
            'Flask-cors'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      calenvite = calenvite.rest:main
      """,
      license='GPLv2',
      packages=find_packages(exclude=['tests']),
      tests_require=[
          'pytest',
          'pytest-cov',
          'pytest-sugar',
          'pytest-catchlog',
          'pytest-datadir-ng',
      ],
      cmdclass={
          'bump': Version,
          'dist_clean': DistClean,
          'test': PyTest
      },
      test_suite="py.test",
      zip_safe=False
      )
