#!/usr/bin/env python
from setuptools import setup, find_packages

requires = ['jinja2', 'pyCLI']

README = open('README.rst').read()

setup(
    name="comicgen",
    py_modules = ('comicgen', ),
    version="0.3",
    url='https://github.com/wutali/comicgen',
    download_url='https://github.com/wutali/comicgen/tarball/master',
    author='Takahiro Fujiwara',
    author_email='email@wuta.li',
    description="A command-line tool to make ebook of comics.",
    long_description=README,
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    classifiers=[],
    entry_points=dict(
        console_scripts=[
            'comicgen = comicgen:comicgen_script',
            'comicgen-volumes = comicgen:comicgen_volumes_script',
        ],
    ),
)
