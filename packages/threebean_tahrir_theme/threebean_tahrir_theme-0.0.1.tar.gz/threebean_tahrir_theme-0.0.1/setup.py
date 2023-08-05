#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

f = open('README.md')
long_description = f.read().strip()
f.close()


requires = []

version = '0.0.1'

setup(
    name='threebean_tahrir_theme',
    version=version,
    description="threebean.org theme for the Tahrir Open Badges webapp",
    long_description=long_description,
    author='Ralph Bean',
    author_email='rbean@redhat.com',
    url='https://github.com/ralphbean/threebean-tahrir-theme',
    license='GPLv3+',
    classifiers=[],
    install_requires=requires,
    packages=['threebean_tahrir_theme'],
    include_package_data=True,
    zip_safe=False,
)
