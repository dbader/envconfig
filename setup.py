import os
import sys
from setuptools import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload -r PyPI')
    sys.exit()

VERSION = '0.2.1'

setup(
    name='envconfig',
    packages=['envconfig'],
    version=VERSION,
    description='Parse config options from the OS environment.',
    long_description=(open('README.rst').read() + '\n\n' +
                      open('HISTORY.rst').read()),
    license="MIT",
    author='Daniel Bader',
    author_email='mail@dbader.org',
    url='https://github.com/dbader/envconfig',
    download_url='https://github.com/dbader/envconfig/tarball/' + VERSION,
    keywords=[
        'config', 'environment', '12factor'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
    ],
)
