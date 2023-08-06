#!/usr/bin/env python
import os
from setuptools import setup


def get_metadata():
    import re
    with open(os.path.join("imagemounter", "__init__.py")) as f:
        return dict(re.findall("__([a-z]+)__ = ['\"]([^'\"]+)['\"]", f.read()))

metadata = get_metadata()

setup(
    name='imagemounter',
    version=metadata['version'],
    packages=['imagemounter'],
    author='Peter Wagenaar, Ralph Broenink',
    author_email='ralph@ralphbroenink.net',
    url='https://github.com/ralphje/imagemounter',
    download_url='https://github.com/ralphje/imagemounter/tarball/v' + metadata['version'],
    description='Utility to mount partitions in Encase, AFF and dd images locally on Linux operating systems.',
    long_description=open("README.md", "r").read(),
    entry_points={'console_scripts': ['imount = imagemounter.mount_images:main']},
    install_requires=['pytsk3', 'termcolor']
)
