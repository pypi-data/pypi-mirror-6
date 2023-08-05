from setuptools import setup
from setuptools.command.test import test as TestCommand
import os
import sys

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
        name='pngrenderer',
        version='0.1.2',
        description='Render matplotlib png images to a zip file',
        author='Simon Walker',
        license=read('LICENSE'),
        author_email='s.r.walker101@gmail.com',
        url='https://github.com/mindriot101/matplotlib-pngrenderer',
        packages=['pngrenderer',],
        install_requires=['matplotlib'],
        long_description=read('README.markdown'),
        tests_require=['pytest'],
        cmdclass={'test': PyTest},
        )
