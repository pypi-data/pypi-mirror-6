import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='shim',
    version='0.1.0',
    description="Vim for Python",
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'License :: Other/Proprietary License',
    ),
    keywords='shim vim emacs',
    author=' ',
    author_email=' ',
    url='https://github.com/swong15/shim',
    package_dir = {'': 'src'},
    packages=find_packages('src', exclude=('ez_setup', 'examples', 'tests')),
    include_package_data=True,
    install_requires=(
        "pygments",
    ),
    cmdclass={'test': PyTest},
    tests_require=(
    ),
    entry_points={
        'console_scripts': [
            'shim = shim:main',
        ],
    }
)
