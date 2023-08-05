from distutils.core import setup
from setuptools.command.test import test as TestCommand
import sys


# The whole Tox business was taken from "Open Sourcing a Python Project the Right Way"
class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)

setup(
    name='luggage',
    version='0.1.2',
    description='A wrapper library for various cloud storage services',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
    ],
    author='Patrick Stegmann (aka. @wonderb0lt)',
    author_email='code@patrick-stegmann.de',
    url='https://github.com/wonderb0lt/luggage',
    packages=['luggage'],
    install_requires=['requests', 'python-dateutil'],
    tests_require=['tox'],
    cmdclass={'test': Tox}
)
