#!/usr/bin/python
# -*- coding: utf-8 -*-

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
from pkg_resources import parse_version
import os
import subprocess as sp

setup(
    name = "CoreNLP-install-models",
    version_command=('git describe --tags', "pep440-git-local"),
    packages = find_packages(),
    setup_requires = ["setuptools-version-command"],
    install_requires = ["plac>=0.9.1", "urwid"],

    # metadata for upload to PyPI
    author = "Karl-Philipp Richter",
    author_email = "krichter722@aol.de",
    url='https://github.com/krichter722/CoreNLP-install-models',
    description = "A script to download Stanford CoreNLP models into a convenient location for a specific operating system",
    license = "GPLv3",
    keywords = "nlp",
)

