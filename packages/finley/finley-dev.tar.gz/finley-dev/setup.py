from setuptools import setup, find_packages

import conf

setup(
    name = "finley",
    version = conf.version,
    packages = find_packages(),
    install_requires = ['MDAnalysis'],
    requires = ['MDAnalysis'],
    provides = ['finley'],
    long_description = '',
    author = "Guido Falk von Rudorff",
    author_email = "guido@vonrudorff.de",
    description = "Command line analyzer for large molecular dynamics trajectories with DCD support.",
    license = "GPL 2",
    keywords = "DCD, PDB, PSF",
    url = "http://guido.vonrudorff.de/finley/",
    classifiers = ['Development Status :: 4 - Beta'],
)