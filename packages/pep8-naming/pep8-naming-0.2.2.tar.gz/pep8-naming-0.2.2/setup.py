# -*- coding: utf-8 -*-
from __future__ import with_statement
from setuptools import setup
from setuptools.command.test import test as TestCommand


def get_version(fname='pep8ext_naming.py'):
    with open(fname) as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])


def get_long_description():
    descr = []
    for fname in ('README.rst',):
        with open(fname) as f:
            descr.append(f.read())
    return '\n\n'.join(descr)


class RunTests(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import run_tests
        import sys
        errno = run_tests.main()
        sys.exit(errno)


setup(
    name='pep8-naming',
    version=get_version(),
    description="Check PEP-8 naming conventions, plugin for flake8",
    long_description=get_long_description(),
    keywords='flake8 pep8 naming',
    author='Florent Xicluna',
    author_email='florent.xicluna@gmail.com',
    url='https://github.com/flintwork/pep8-naming',
    license='Expat license',
    py_modules=['pep8ext_naming'],
    zip_safe=False,
    entry_points={
        'flake8.extension': [
            'N80 = pep8ext_naming:NamingChecker',
            'N81 = pep8ext_naming:NamingChecker',
        ],
        # Backward compatibility for Flint (now merged into Flake8)
        'flint.extension': [
            'N80 = pep8ext_naming:NamingChecker',
            'N81 = pep8ext_naming:NamingChecker',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
    ],
    cmdclass={'test': RunTests},
)
