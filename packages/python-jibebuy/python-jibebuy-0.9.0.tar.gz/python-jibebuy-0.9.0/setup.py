#!/usr/bin/python2.4
#
# Copyright 1014 Jibebuy, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'support@jibebuy.com'
__version__ = '0.9.0'


# The base package metadata to be used by both distutils and setuptools
METADATA = dict(
    name = "python-jibebuy",
    version = __version__,
    py_modules = ['jibebuy'],
    author='Jibebuy, Inc.',
    author_email='support@jibebuy.com.',
    description='A python wrapper for the Jibebuy REST API',
    license='Apache License 2.0',
    url='https://github.com/pjtpj/python-jibebuy',
    keywords='jibebuy api',
)

# Extra package metadata to be used only if setuptools is installed
SETUPTOOLS_METADATA = dict(
    install_requires = ['setuptools', 'requests'],
    include_package_data = True,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
    ],
    test_suite = 'jibebuy_test.suite',
)


def Read(file):
    return open(file).read()


def BuildLongDescription():
    return '\n'.join([Read('README.md'), Read('CHANGES')])


def Main():
    # Build the long_description from the README and CHANGES
    METADATA['long_description'] = BuildLongDescription()

    # Use setuptools if available, otherwise fallback and use distutils
    try:
        import setuptools
        METADATA.update(SETUPTOOLS_METADATA)
        setuptools.setup(**METADATA)
    except ImportError:
        import distutils.core
        distutils.core.setup(**METADATA)


if __name__ == '__main__':
    Main()
