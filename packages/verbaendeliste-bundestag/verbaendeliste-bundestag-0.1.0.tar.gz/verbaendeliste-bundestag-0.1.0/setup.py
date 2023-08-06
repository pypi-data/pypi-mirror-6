#!/usr/bin/env python

import codecs
import re
import os

from setuptools import setup


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="verbaendeliste-bundestag",
    version=find_version("verbaendeliste_bundestag.py"),
    url='https://github.com/stefanw/verbaendeliste-bundestag',
    license='MIT',
    description="Parse PDF-to-XML converted lobby list of German Bundestag",
    long_description=read('README.md'),
    author='Stefan Wehrmeyer',
    author_email='mail@stefanwehrmeyer.com',
    py_modules=['verbaendeliste_bundestag'],
    install_requires=[],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7'
    ]
)
