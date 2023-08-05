import sys
import os
import codecs

from setuptools import setup, find_packages


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

VERSION = "0.0.4"

with codecs.open('README.rst', encoding='utf-8') as f:
    README = f.read()

with codecs.open('CHANGELOG.rst', encoding='utf-8') as f:
    CHANGELOG = f.read()

setup(
    name='puppetboard',
    version=VERSION,
    author='Daniele Sluijters',
    author_email='daniele.sluijters+pypi@gmail.com',
    packages=find_packages(),
    url='https://github.com/nedap/puppetboard',
    license='Apache License 2.0',
    description='Web frontend for PuppetDB',
    include_package_data=True,
    long_description='\n'.join((README, CHANGELOG)),
    install_requires=[
        "Flask >= 0.10.1",
        "Flask-WTF >= 0.9.4",
        "pypuppetdb >= 0.1.0",
        ],
    keywords="puppet puppetdb puppetboard",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        ],
)
