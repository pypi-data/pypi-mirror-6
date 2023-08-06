from setuptools import setup
from setuptools.command.test import test as TestCommand
import os
import sys


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


def read(fname):
    """
    Utility function to read the README file.
    Used for the long_description.  It's nice, because now 1) we have a
    top level README file and 2) it's easier to type in the README file
    than to put a raw string in below ...
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

tests_require = [
    'coverage==3.7.1',
    'flake8==2.1.0',
    'mock==1.0.1',
    'nose==1.3.1',
    'requests==2.2.1',
    'tox==1.7.1',
],

install_requires = [
    'six==1.6.1',
    'tornado==3.2',
]

setup(
    author="Asim Ihsan",
    author_email="asim.ihsan@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    cmdclass={'test': Tox},
    description="An HTTP-controlled process runner and results gatherer",
    entry_points={
        'console_scripts': [
            'vocalsalad = vocalsalad.server:main',
        ],
    },
    install_requires=install_requires,
    keywords="http command process execute",
    license="MIT",
    long_description=read('README.md'),
    name="vocalsalad",
    package_dir={'': 'vocalsalad'},
    tests_require=tests_require,
    url="https://github.com/asimihsan/vocalsalad",
    version="0.0.1",
    zip_safe=False,
)
